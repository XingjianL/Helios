#include "PlantArchitecture.h"
#include "RadiationModel.h"
#include "VoxelIntersection.h"
#include <asio.hpp>
#include <bson/bson.h>

using namespace helios;
std::vector<uint8_t> build_advertise_bson(const std::string& topic,
                                        const std::string& type)
{
    bson_t* doc = bson_new();

    BSON_APPEND_UTF8(doc, "op", "advertise");
    BSON_APPEND_UTF8(doc, "topic", topic.c_str());

    BSON_APPEND_UTF8(doc, "type", type.c_str());

    // Copy raw BSON (NO PREFIX!)
    uint32_t bson_size = doc->len;
    const uint8_t* bson_bytes = bson_get_data(doc);

    std::vector<uint8_t> packet(bson_bytes, bson_bytes + bson_size);

    bson_destroy(doc);
    return packet;
}
std::vector<uint8_t> build_publish_bson(const std::string& topic,
                                        const std::string& data)
{
    bson_t* doc = bson_new();

    BSON_APPEND_UTF8(doc, "op", "publish");
    BSON_APPEND_UTF8(doc, "topic", topic.c_str());

    bson_t child;
    BSON_APPEND_DOCUMENT_BEGIN(doc, "msg", &child);
    BSON_APPEND_UTF8(&child, "data", data.c_str());
    bson_append_document_end(doc, &child);

    // Copy raw BSON (NO PREFIX!)
    uint32_t bson_size = doc->len;
    const uint8_t* bson_bytes = bson_get_data(doc);

    std::vector<uint8_t> packet(bson_bytes, bson_bytes + bson_size);

    bson_destroy(doc);
    return packet;
}
std::vector<uint8_t> build_publish_bson_string(const std::string& topic, const std::string& data) {
    bson_t* doc = bson_new();

    BSON_APPEND_UTF8(doc, "op", "publish");
    BSON_APPEND_UTF8(doc, "topic", topic.c_str());

    bson_t child;
    BSON_APPEND_DOCUMENT_BEGIN(doc, "msg", &child);
    BSON_APPEND_UTF8(&child, "file_contents", data.c_str());
    bson_append_document_end(doc, &child);

    uint32_t bson_size = doc->len;
    const uint8_t* bson_bytes = bson_get_data(doc);

    std::vector<uint8_t> packet(bson_bytes, bson_bytes + bson_size);
    bson_destroy(doc);
    return packet;
}
std::string read_file(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file: " + path);
    }
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}
std::vector<uint8_t> build_subscribe_bson(const std::string& topic,
                                          const std::string& type = "")
{
    bson_t* doc = bson_new();

    BSON_APPEND_UTF8(doc, "op", "subscribe");
    BSON_APPEND_UTF8(doc, "topic", topic.c_str());

    if (!type.empty()) {
        BSON_APPEND_UTF8(doc, "type", type.c_str());
    }

    // Copy raw BSON
    uint32_t bson_size = doc->len;
    const uint8_t* bson_bytes = bson_get_data(doc);

    std::vector<uint8_t> packet(bson_bytes, bson_bytes + bson_size);
    bson_destroy(doc);
    return packet;
}
std::vector<uint8_t> build_unsubscribe_bson(const std::string& topic)
{
    bson_t* doc = bson_new();

    BSON_APPEND_UTF8(doc, "op", "unsubscribe");
    BSON_APPEND_UTF8(doc, "topic", topic.c_str());

    // Copy raw BSON
    uint32_t bson_size = doc->len;
    const uint8_t* bson_bytes = bson_get_data(doc);

    std::vector<uint8_t> packet(bson_bytes, bson_bytes + bson_size);
    bson_destroy(doc);
    return packet;
}
std::string read_bson_until(
    asio::ip::tcp::socket& socket,
    asio::io_context& io_context,
    const std::string& find_string,
    std::chrono::milliseconds timeout,
    const std::size_t buffer_size = 4096)
{
    std::vector<uint8_t> buffer(buffer_size);
    std::string last_json;

    asio::steady_timer timer(io_context);
    bool finished = false;
    bool timeout_occurred = false;

    // Start read loop
    std::function<void()> start_read = [&]() {

        socket.async_read_some(asio::buffer(buffer),
            [&](const asio::error_code& ec, std::size_t len)
            {
                if (timeout_occurred) return;

                if (ec) {
                    std::cerr << "Socket read error: " << ec.message() << "\n";
                    finished = true;
                    return;
                }
                timer.expires_after(timeout);
                bson_t* doc = bson_new_from_data(buffer.data(), len);
                if (!doc) {
                    std::cerr << "Invalid BSON received\n";
                    start_read();
                    return;
                }

                char* str = bson_as_canonical_extended_json(doc, nullptr);
                last_json = str;

                std::cout << "Received: " << last_json << "\n";

                bool match = last_json.find(find_string) != std::string::npos;

                bson_free(str);
                bson_destroy(doc);

                if (match) {
                    finished = true;
                    timer.cancel();
                    return;
                }

                // Keep reading
                start_read();
            }
        );
    };

    // Start timer
    timer.expires_after(timeout);
    timer.async_wait([&](const asio::error_code& ec) {
        if (!ec) {
            timeout_occurred = true;
            socket.cancel();
        }
    });

    // Start the first async read
    start_read();

    // Run until read finishes or timeout fires
    io_context.run();
    io_context.restart();

    if (timeout_occurred) {
        std::cerr << "Read timed out after "
                  << timeout.count() << " ms\n";
        return "";
    }

    return last_json;
}

int main(int argc, char **argv) {
    // Open a socket to the ROSBridge server
    asio::io_context io_context;
    asio::ip::tcp::socket socket(io_context);
    asio::ip::tcp::endpoint endpoint(
        asio::ip::make_address("172.20.218.12"),
        9090
    );
    socket.connect(endpoint);
    std::cout << "Connected\n";
    // Send test messages and set up subscriptions
    auto packet = build_advertise_bson("/my_string", "std_msgs/String");
    asio::write(socket, asio::buffer(packet));
    packet = build_publish_bson("/my_string", "Hello from BSON + ASIO");
    asio::write(socket, asio::buffer(packet));
    std::cout << "Message sent\n";
    packet = build_advertise_bson("/ue5/game_commands", "std_msgs/String");
    asio::write(socket, asio::buffer(packet));
    std::chrono::milliseconds duration(1000);
    packet = build_subscribe_bson("/ue5/LoadModel", "std_msgs/String");
    asio::write(socket, asio::buffer(packet));


    // configure the Helios procedural model framework
    Context context;
    PlantArchitecture plantarchitecture(&context);
    context.seedRandomGenerator(10);                            // Seed
    plantarchitecture.loadPlantModelFromLibrary("tomato");      // plant model
    vec3 canopy_center(0.f, 0.f, 0.f);
    vec2 plant_spacing(0.5f, 0.5f);                             // plant spacing (meters)
    int2 plant_count(1, 1);                                     // number of plants
    const size_t CHUNK_SIZE = 64 * 1024;                        // mesh data packet size
    float plant_age = 7.f;                                      // gap days
    plantarchitecture.buildPlantCanopyFromLibrary(canopy_center, plant_spacing, plant_count, 74.f); // build the canopy at the start date

    // shade parameters
    vec2 canopy_extent(3,3);
    //std::vector<uint> UUIDs_ground = context.addTile(make_vec3(0, 0, 0), canopy_extent, nullrotation,make_int2(10, 10));
    vec3 sun_direction(1,0,1);                              //Cartesian unit vector pointing in the direction of (toward) the sun
    sun_direction.normalize();

    

    //context.setPrimitiveData(UUIDs_ground, "twosided_flag",uint(0));
    for (int i = 0; i < 1; i++) {
        // generate the plant as it ages
        // indicate the obj to be reset
        packet = build_publish_bson("/ue5/game_commands", "OBJClear:OBJClear");
        asio::write(socket, asio::buffer(packet));
        std::string result = read_bson_until(
            socket,
            io_context,
            "OBJCleared",                        // search for this
            std::chrono::milliseconds(5000), // timeout
            CHUNK_SIZE
        );

        if (result.empty()) {
            std::cout << "Timed out or error\n";
            std::exit(1);
        } else {
            std::cout << "Final matched JSON:\n" << result << "\n";
        }

        context.writeOBJ("test.obj");

        // remove the previous merged mesh
        std::remove("test_merge.obj");
        // optimize and merge the generated mesh
        std::string command = "python3 preprocess_mesh.py --input_obj test.obj --output_obj test_merge.obj";
        std::system(command.c_str());
        while (!std::filesystem::exists("test_merge.obj")) {
            std::cout << "Waiting file preprocess\n";
        }
        // send the mesh MTL data
        auto file_data = read_file("test.mtl");
        file_data = "MTLData:" + file_data;
        packet = build_publish_bson("/ue5/game_commands", file_data);
        asio::write(socket, asio::buffer(packet));
        std::cout << "Mesh MTL sent\n";
        result = read_bson_until(
            socket,
            io_context,
            "MTLReceived",                        // search for this
            std::chrono::milliseconds(5000), // timeout
            CHUNK_SIZE
        );

        if (result.empty()) {
            std::cout << "Timed out or error\n";
            std::exit(1);
        } else {
            std::cout << "Final matched JSON:\n" << result << "\n";
        }

        // send the mesh OBJ data
        
        file_data = read_file("test_merge.obj");
        std::vector<std::string> chunks;
        for (size_t obj_byte = 0; obj_byte < file_data.size(); obj_byte += CHUNK_SIZE) {
            chunks.push_back(file_data.substr(obj_byte, CHUNK_SIZE));
        }
        for (size_t chunk_idx = 0; chunk_idx < chunks.size(); chunk_idx++) {
            file_data = "OBJData:" + chunks[chunk_idx];
            packet = build_publish_bson("/ue5/game_commands", file_data);
            asio::write(socket, asio::buffer(packet));
            std::cout << "Mesh OBJ sending:"<< chunk_idx << " total: " << chunks.size() << "\n";
            result = read_bson_until(
                socket,
                io_context,
                "OBJReceived",                        // search for this
                std::chrono::milliseconds(5000), // timeout
                CHUNK_SIZE
            );

            if (result.empty()) {
                std::cout << "Timed out or error\n";
                std::exit(1);
            } else {
                std::cout << "Final matched JSON:\n" << result << "\n";
            }
        }
        
        
        packet = build_publish_bson("/ue5/game_commands", "OBJFinished:OBJFinished");
        asio::write(socket, asio::buffer(packet));
        std::cout << "Mesh OBJ finished\n";

        result = read_bson_until(
            socket,
            io_context,
            "true",                        // search for this
            std::chrono::milliseconds(1000), // timeout
            CHUNK_SIZE
        );

        if (result.empty()) {
            std::cout << "Timed out or error\n";
            std::exit(1);
        } else {
            std::cout << "Final matched JSON:\n" << result << "\n";
        }
        
        // compute the plant shade using helios
        for (int lightPos = 0; lightPos < 100; lightPos++){
            std::vector<uint> UUIDs_leaves = plantarchitecture.getAllLeafUUIDs();

            // radiation par sunlit
            RadiationModel radiation(&context);
            radiation.addRadiationBand("PAR");

            uint sourceID = radiation.addCollimatedRadiationSource( sun_direction );
            double light_angle = 2.0 * 3.14159265358 * lightPos / 100; // evenly spaced angles
            vec3 supplementary_light(1.25 * cos(light_angle), 1.25 * sin(light_angle), 1.8f);
            std::cout << "Light angle: " << light_angle << std::endl;
            uint lightID = radiation.addSphereRadiationSource(supplementary_light, 1.f);
            radiation.setSourceFlux(lightID, "PAR", 0.15f);

            radiation.disableEmission("PAR");
            radiation.setSourceFlux(sourceID, "PAR", 1.f);  //set a flux of 1.0 W/m^2 to simplify calculations
            radiation.setDiffuseRadiationFlux("PAR", 0.f);
            radiation.enforcePeriodicBoundary("xy");

            
            radiation.updateGeometry();
            radiation.runBand("PAR");

            //radiation.deleteRadiationSource(lightID);
            // 4a. Calculate G(theta)
            
            float Gtheta = 0;
            float area_total = 0;
            for( auto UUID : UUIDs_leaves ){
                vec3 normal = context.getPrimitiveNormal(UUID);
                float area = context.getPrimitiveArea(UUID);
                Gtheta += std::abs( sun_direction*normal )*area;
                area_total += area;
            }
            Gtheta = Gtheta/area_total;  //normalize
            
            //std::cout << "G(theta) = " << Gtheta << std::endl;
            // 4b. Calculate radiation flux absorbed by the canopy on a ground area basis - this will end up just being the area-weighted average PAR flux multiplied by LAI.
            
            float PAR_abs_dir;
            context.calculatePrimitiveDataAreaWeightedMean( UUIDs_leaves, "radiation_flux_PAR", PAR_abs_dir ); //recall that the output primitive data from the radiation model has the form "radiation_flux_[*band_name*]"
            float LAI = plantarchitecture.sumPlantLeafArea(0);
            std::cout << "LAI: " << LAI << std::endl;
            PAR_abs_dir = PAR_abs_dir*LAI; //converts between leaf area basis to ground area basis
            
            // 4c. Calculate the theoretical absorbed PAR flux using Beer's law
            
            float theta_s = cart2sphere(sun_direction).zenith;  //calculate the solar zenith angle
            
            float R0 = cos(theta_s); //PAR flux on horizontal surface
            float intercepted_theoretical_direct = R0*(1.f-exp(-Gtheta*LAI/cos(theta_s)));  //Beer's law
            
            std::cout << "Calculated interception: " << PAR_abs_dir << std::endl;
            //std::cout << "Theoretical interception: " << intercepted_theoretical_direct << std::endl;
            //std::cout << "Error of interception: " << std::abs(PAR_abs_dir-intercepted_theoretical_direct)/intercepted_theoretical_direct*100.f << " %" << std::endl;
            float sunlit_area = 0;
            float total_area = 0;
            for( auto UUID : UUIDs_leaves ){ //looping over all leaf elements
            
                vec3 normal = context.getPrimitiveNormal(UUID);
            
                float PARmax = std::abs( normal*sun_direction );  //this is the PAR flux of a leaf with the same normal that is fully sunlit
            
                float PAR;
                context.getPrimitiveData( UUID, "radiation_flux_PAR", PAR ); //get this leaf's PAR flux
            
                float fsun_leaf = PAR/PARmax;  //PAR flux as a fraction of the fully sunlit flux
            
                float area = context.getPrimitiveArea(UUID);
            
                if( fsun_leaf>0.5 ){ //if fsun is greater than 0.5, we'll call this leaf "sunlit"
                    sunlit_area += area;
                }
                total_area += area;
            
            }
            
            float fsun = sunlit_area/total_area;
            
            // 4e. Calculate the theoretical sunlit area fraction
            
            float fsun_theoretical = cos(theta_s)/(Gtheta*LAI)*(1-exp(-Gtheta*LAI/cos(theta_s)));
            
            std::cout << "Calculated sunlit fraction: " << fsun << std::endl;
            //std::cout << "Theoretical sunlit fraction: " << fsun_theoretical << std::endl;
            //std::cout << "Error of sunlit fraction: " << std::abs(fsun-fsun_theoretical)/fsun_theoretical*100.f << " %" << std::endl;
        }
        // packet = build_unsubscribe_bson("/ue5/LoadModel");
        // asio::write(socket, asio::buffer(packet));
        // grow the plant
        plantarchitecture.advanceTime(plant_age);

        // wait until the simulation is done with the sent plant
        result = read_bson_until(
            socket,
            io_context,
            "NextAge",                        // search for this
            std::chrono::hours(24), // timeout
            CHUNK_SIZE
        );

        if (result.empty()) {
            std::cout << "Timed out or error\n";
            std::exit(1);
        } else {
            std::cout << "Final matched JSON:\n" << result << "\n";
        }
    }
    
    

    //plantarchitecture.writePlantMeshVertices
    
    


}