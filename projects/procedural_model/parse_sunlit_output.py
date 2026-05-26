import re
import pandas as pd

log_text = """
Light angle: 0
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.028446
Calculated sunlit fraction: 0.810232
Light angle: 0.0628319
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284939
Calculated sunlit fraction: 0.812704
Light angle: 0.125664
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285216
Calculated sunlit fraction: 0.816297
Light angle: 0.188496
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285643
Calculated sunlit fraction: 0.809554
Light angle: 0.251327
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285366
Calculated sunlit fraction: 0.807056
Light angle: 0.314159
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284854
Calculated sunlit fraction: 0.811193
Light angle: 0.376991
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.028544
Calculated sunlit fraction: 0.810908
Light angle: 0.439823
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285057
Calculated sunlit fraction: 0.814735
Light angle: 0.502655
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284907
Calculated sunlit fraction: 0.815409
Light angle: 0.565487
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285875
Calculated sunlit fraction: 0.816632
Light angle: 0.628319
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284937
Calculated sunlit fraction: 0.809274
Light angle: 0.69115
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284863
Calculated sunlit fraction: 0.810736
Light angle: 0.753982
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.028455
Calculated sunlit fraction: 0.813132
Light angle: 0.816814
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285269
Calculated sunlit fraction: 0.811475
Light angle: 0.879646
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285057
Calculated sunlit fraction: 0.808983
Light angle: 0.942478
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285509
Calculated sunlit fraction: 0.813722
Light angle: 1.00531
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285023
Calculated sunlit fraction: 0.813787
Light angle: 1.06814
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285137
Calculated sunlit fraction: 0.815757
Light angle: 1.13097
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285151
Calculated sunlit fraction: 0.812297
Light angle: 1.19381
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285089
Calculated sunlit fraction: 0.813592
Light angle: 1.25664
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285191
Calculated sunlit fraction: 0.811731
Light angle: 1.31947
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285136
Calculated sunlit fraction: 0.808143
Light angle: 1.3823
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.028514
Calculated sunlit fraction: 0.813127
Light angle: 1.44513
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284999
Calculated sunlit fraction: 0.812967
Light angle: 1.50796
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285106
Calculated sunlit fraction: 0.814036
Light angle: 1.5708
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285343
Calculated sunlit fraction: 0.813313
Light angle: 1.63363
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285268
Calculated sunlit fraction: 0.812569
Light angle: 1.69646
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284832
Calculated sunlit fraction: 0.809316
Light angle: 1.75929
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285408
Calculated sunlit fraction: 0.808886
Light angle: 1.82212
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.028483
Calculated sunlit fraction: 0.813055
Light angle: 1.88496
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285255
Calculated sunlit fraction: 0.814454
Light angle: 1.94779
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285008
Calculated sunlit fraction: 0.815787
Light angle: 2.01062
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285238
Calculated sunlit fraction: 0.809052
Light angle: 2.07345
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284911
Calculated sunlit fraction: 0.811378
Light angle: 2.13628
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284867
Calculated sunlit fraction: 0.816405
Light angle: 2.19911
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285394
Calculated sunlit fraction: 0.81423
Light angle: 2.26195
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285242
Calculated sunlit fraction: 0.811259
Light angle: 2.32478
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285419
Calculated sunlit fraction: 0.808232
Light angle: 2.38761
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285373
Calculated sunlit fraction: 0.812301
Light angle: 2.45044
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285049
Calculated sunlit fraction: 0.811989
Light angle: 2.51327
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285036
Calculated sunlit fraction: 0.817616
Light angle: 2.57611
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285015
Calculated sunlit fraction: 0.810218
Light angle: 2.63894
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285293
Calculated sunlit fraction: 0.816933
Light angle: 2.70177
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284949
Calculated sunlit fraction: 0.813812
Light angle: 2.7646
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284644
Calculated sunlit fraction: 0.816929
Light angle: 2.82743
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284799
Calculated sunlit fraction: 0.810924
Light angle: 2.89027
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285054
Calculated sunlit fraction: 0.813501
Light angle: 2.9531
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285112
Calculated sunlit fraction: 0.812338
Light angle: 3.01593
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284892
Calculated sunlit fraction: 0.810814
Light angle: 3.07876
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285311
Calculated sunlit fraction: 0.812775
Light angle: 3.14159
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284967
Calculated sunlit fraction: 0.812631
Light angle: 3.20442
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285062
Calculated sunlit fraction: 0.813527
Light angle: 3.26726
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285099
Calculated sunlit fraction: 0.814513
Light angle: 3.33009
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.028531
Calculated sunlit fraction: 0.815059
Light angle: 3.39292
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284932
Calculated sunlit fraction: 0.81349
Light angle: 3.45575
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285334
Calculated sunlit fraction: 0.817384
Light angle: 3.51858
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.028514
Calculated sunlit fraction: 0.814818
Light angle: 3.58142
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285183
Calculated sunlit fraction: 0.814033
Light angle: 3.64425
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.028472
Calculated sunlit fraction: 0.812033
Light angle: 3.70708
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285297
Calculated sunlit fraction: 0.816671
Light angle: 3.76991
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284462
Calculated sunlit fraction: 0.810035
Light angle: 3.83274
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285042
Calculated sunlit fraction: 0.818112
Light angle: 3.89557
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285449
Calculated sunlit fraction: 0.813289
Light angle: 3.95841
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285215
Calculated sunlit fraction: 0.812105
Light angle: 4.02124
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284883
Calculated sunlit fraction: 0.810563
Light angle: 4.08407
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285153
Calculated sunlit fraction: 0.812523
Light angle: 4.1469
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284603
Calculated sunlit fraction: 0.806085
Light angle: 4.20973
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285042
Calculated sunlit fraction: 0.812482
Light angle: 4.27257
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284848
Calculated sunlit fraction: 0.808749
Light angle: 4.3354
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285153
Calculated sunlit fraction: 0.812107
Light angle: 4.39823
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285467
Calculated sunlit fraction: 0.811286
Light angle: 4.46106
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285104
Calculated sunlit fraction: 0.815998
Light angle: 4.52389
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285197
Calculated sunlit fraction: 0.811809
Light angle: 4.58673
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285364
Calculated sunlit fraction: 0.809919
Light angle: 4.64956
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285226
Calculated sunlit fraction: 0.819318
Light angle: 4.71239
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285156
Calculated sunlit fraction: 0.809479
Light angle: 4.77522
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285332
Calculated sunlit fraction: 0.806175
Light angle: 4.83805
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.028495
Calculated sunlit fraction: 0.818277
Light angle: 4.90088
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284801
Calculated sunlit fraction: 0.812133
Light angle: 4.96372
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285122
Calculated sunlit fraction: 0.815198
Light angle: 5.02655
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284796
Calculated sunlit fraction: 0.812473
Light angle: 5.08938
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284527
Calculated sunlit fraction: 0.80822
Light angle: 5.15221
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285371
Calculated sunlit fraction: 0.809213
Light angle: 5.21504
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285234
Calculated sunlit fraction: 0.807433
Light angle: 5.27788
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285162
Calculated sunlit fraction: 0.815193
Light angle: 5.34071
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285079
Calculated sunlit fraction: 0.815051
Light angle: 5.40354
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284689
Calculated sunlit fraction: 0.807318
Light angle: 5.46637
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284917
Calculated sunlit fraction: 0.811819
Light angle: 5.5292
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285287
Calculated sunlit fraction: 0.811441
Light angle: 5.59203
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285346
Calculated sunlit fraction: 0.811019
Light angle: 5.65487
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284728
Calculated sunlit fraction: 0.810337
Light angle: 5.7177
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285126
Calculated sunlit fraction: 0.815798
Light angle: 5.78053
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284769
Calculated sunlit fraction: 0.811939
Light angle: 5.84336
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285569
Calculated sunlit fraction: 0.811225
Light angle: 5.90619
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285241
Calculated sunlit fraction: 0.810967
Light angle: 5.96903
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285298
Calculated sunlit fraction: 0.809753
Light angle: 6.03186
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285027
Calculated sunlit fraction: 0.811546
Light angle: 6.09469
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0285057
Calculated sunlit fraction: 0.814944
Light angle: 6.15752
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284814
Calculated sunlit fraction: 0.813099
Light angle: 6.22035
Updating geometry in radiation transport model...done.
Updating radiative properties...done
Performing primary direct radiation ray trace for bands PAR, ...done.                                                          
LAI: 0.0622821
Calculated interception: 0.0284846
Calculated sunlit fraction: 0.811753
"""

# Regex patterns
angle_re = re.compile(r"Light angle:\s*([0-9.eE+-]+)")
lai_re = re.compile(r"LAI:\s*([0-9.eE+-]+)")
interception_re = re.compile(r"Calculated interception:\s*([0-9.eE+-]+)")
sunlit_re = re.compile(r"Calculated sunlit fraction:\s*([0-9.eE+-]+)")

angles = angle_re.findall(log_text)
lais = lai_re.findall(log_text)
interceptions = interception_re.findall(log_text)
sunlits = sunlit_re.findall(log_text)

# Safety check
n = min(len(angles), len(lais), len(interceptions), len(sunlits))

df = pd.DataFrame({
    "light_angle_rad": [float(a) for a in angles[:n]],
    "LAI": [float(l) for l in lais[:n]],
    "interception": [float(i) for i in interceptions[:n]],
    "sunlit_fraction": [float(s) for s in sunlits[:n]],
})

print(df)
