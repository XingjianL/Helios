#include "PlantArchitecture.h"
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
    context.seedRandomGenerator(10);
    plantarchitecture.loadPlantModelFromLibrary("tomato");
    vec3 canopy_center(0.f, 0.f, 0.f);
    vec2 plant_spacing(0.5f, 0.5f);
    int2 plant_count(1, 1);
    const size_t CHUNK_SIZE = 64 * 1024;
    float plant_age = 7.f; // days
    plantarchitecture.buildPlantCanopyFromLibrary(canopy_center, plant_spacing, plant_count, 28.f);
    for (int i = 0; i < 10; i++) {
        // generate the plant as it ages
        
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
        
        // packet = build_unsubscribe_bson("/ue5/LoadModel");
        // asio::write(socket, asio::buffer(packet));
        plantarchitecture.advanceTime(plant_age);
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
        // packet = build_subscribe_bson("/ue5/game_commands", "std_msgs/String");
        // asio::write(socket, asio::buffer(packet));
        // while (true) {
        //     uint8_t buffer[4096];

        //     asio::error_code ec;
        //     size_t len = socket.read_some(asio::buffer(buffer), ec);

        //     if (ec) {
        //         std::cerr << "Socket read error: " << ec.message() << "\n";
        //         break;
        //     }

        //     bson_t* doc = bson_new_from_data(buffer, len);
        //     if (!doc) {
        //         std::cerr << "Invalid BSON received\n";
        //         continue;
        //     }

        //     // Print what arrived
        //     char* str = bson_as_canonical_extended_json(doc, nullptr);
        //     std::string json(str);
        //     std::cout << "Received: " << json << "\n";
        //     if (json.find("NextAge") != std::string::npos) {
        //         bson_free(str);
        //         bson_destroy(doc);
        //         break;
        //     }
        //     bson_free(str);
        //     bson_destroy(doc);

        // }
        // packet = build_unsubscribe_bson("/ue5/game_commands");
        // asio::write(socket, asio::buffer(packet));
        // packet = build_subscribe_bson("/ue5/LoadModel", "std_msgs/String");
        // asio::write(socket, asio::buffer(packet));
    }
    
    

    //plantarchitecture.writePlantMeshVertices
    
    


}