import cv2 as cv
import numpy as np
# Assurez-vous que code2.py est dans le même répertoire et contient :
# - fullContoursProcess(image) : Fonction qui détecte les motifs et peuple code2.center_tab (liste de (x, y, type_motif))
# - angleRedPattern(image) : Fonction qui détecte le motif rouge (centre) et retourne son angle
# - Une variable globale code2.center_tab
# - Une variable globale code2.transformed_mire utilisée par fullContoursProcess
import code2
import math

# === PARAMÈTRES ===
image_original_path = "mire_315a.png" # Utilisée principalement pour la taille de sortie
image_transformed_path = "data/trans.png"
distance_init = 5  # Distance de départ pour la recherche de voisins
step_size = 5      # Pas d'augmentation de la distance lors de la recherche de voisins
max_distance = 100  # Limite maximale de recherche de voisins (en pixels)

# === TABLEAUX DE DONNEES MOTEUR (Bases de référence de la mire originale) ===
# Colle ici les listes base_mire_0, base_mire_90, base_mire_180, base_mire_270.

# --- Début de tes listes base_mire_X ---

base_mire_0 = [
('(255, 255)', '120121210'),
('(287, 255)', '102112220'),
('(255, 287)', '212011100'),
('(223, 255)', '102022112'),
('(255, 223)', '111201021'),
('(287, 287)', '001211202'),
('(223, 287)', '021201121'),
('(287, 223)', '211110122'),
('(223, 223)', '210210111'),
('(255, 319)', '121202002'),
('(319, 255)', '200122102'),
('(191, 255)', '021102210'),
('(255, 191)', '112002002'),
('(287, 319)', '022120020'),
('(319, 287)', '020012022'),
('(223, 319)', '211120212'),
('(319, 223)', '221201210'),
('(287, 191)', '021120112'),
('(191, 287)', '211110102'),
('(223, 191)', '022110211'),
('(191, 223)', '201001021'),
('(319, 319)', '202000222'),
('(191, 319)', '110112021'),
('(319, 191)', '122001121'),
('(191, 191)', '120021002'),
('(351, 255)', '020221011'),
('(255, 351)', '212121022'),
('(159, 255)', '110210202'),
('(255, 159)', '210012000'),
('(287, 351)', '221210202'),
('(351, 287)', '222020112'),
('(223, 351)', '121112121'),
('(351, 223)', '102212001'),
('(287, 159)', '001220011'),
('(159, 287)', '111021021'),
('(159, 223)', '012120120'),
('(223, 159)', '001121221'),
('(319, 351)', '022202221'),
('(351, 319)', '220202121'),
('(191, 351)', '112011212'),
('(351, 191)', '212111200'),
('(159, 319)', '100101211'),
('(319, 159)', '110000012'),
('(159, 191)', '001212112'),
('(191, 159)', '110222100'),
('(255, 383)', '100212220'),
('(383, 255)', '112010100'),
('(127, 255)', '200011011'),
('(255, 127)', '220100200'),
('(383, 287)', '122201001'),
('(287, 383)', '200122022'),
('(383, 223)', '010120010'),
('(223, 383)', '202111210'),
('(127, 287)', '012002111'),
('(287, 127)', '002202201'),
('(127, 223)', '120122001'),
('(223, 127)', '101200022'),
('(351, 351)', '212022211'),
('(159, 351)', '021011111'),
('(351, 159)', '121100220'),
('(159, 159)', '202122211'),
('(319, 383)', '220220211'),
('(383, 319)', '212221012'),
('(383, 191)', '001212101'),
('(191, 383)', '121201120'),
('(319, 127)', '010022201'),
('(127, 319)', '102200110'),
('(127, 191)', '211221200'),
('(191, 127)', '212210010'),
('(351, 383)', '112202111'),
('(383, 351)', '111222121'),
('(255, 415)', '011021200'),
('(415, 255)', '001101112'),
('(159, 383)', '210100112'),
('(383, 159)', '202102110'),
('(127, 351)', '010221102'),
('(351, 127)', '011022022'),
('(95, 255)', '001021120'),
('(255, 95)', '021001120'),
('(127, 159)', '122212220'),
('(159, 127)', '221201021'),
('(287, 415)', '001012221'),
('(415, 287)', '012110122'),
('(223, 415)', '012212101'),
('(415, 223)', '101000111'),
('(95, 287)', '022100201'),
('(287, 95)', '202011220'),
('(223, 95)', '012010102'),
('(95, 223)', '100212212'),
('(415, 319)', '121210220'),
('(319, 415)', '210022110'),
('(415, 191)', '010021011'),
('(191, 415)', '221121201'),
('(95, 319)', '222210010'),
('(319, 95)', '200212020'),
('(191, 95)', '022111001'),
('(95, 191)', '212112121'),
('(383, 383)', '111121210'),
('(127, 383)', '101020021'),
('(383, 127)', '221020211'),
('(127, 127)', '212100122'),
('(351, 415)', '101221112'),
('(415, 351)', '211121202'),
('(159, 415)', '111012122'),
('(415, 159)', '100221001'),
('(95, 351)', '202222101'),
('(351, 95)', '200220102'),
('(159, 95)', '122011102'),
('(95, 159)', '221121212'),
('(255, 447)', '121100001'),
('(447, 255)', '120011011'),
('(63, 255)', '012102100'),
('(255, 63)', '100010212'),
('(287, 447)', '012100211'),
('(447, 287)', '221001110'),
('(223, 447)', '110220012'),
('(447, 223)', '110101001'),
('(63, 287)', '122210002'),
('(287, 63)', '120102222'),
('(223, 63)', '000121010'),
('(63, 223)', '201001210'),
('(319, 447)', '111002102'),
('(447, 319)', '202102101'),
('(447, 191)', '111010200'),
('(191, 447)', '201112011'),
('(63, 319)', '221221022'),
('(319, 63)', '222122102'),
('(383, 415)', '120111101'),
('(415, 383)', '101112022'),
('(63, 191)', '120011221'),
('(191, 63)', '101112100'),
('(127, 415)', '010101211'),
('(415, 127)', '112202200'),
('(95, 383)', '010222010'),
('(383, 95)', '020201221'),
('(127, 95)', '021001112'),
('(95, 127)', '121210021'),
('(351, 447)', '021121121'),
('(447, 351)', '021212011'),
('(447, 159)', '010110220'),
('(159, 447)', '112101220'),
('(351, 63)', '022221210'),
('(63, 351)', '222122220'),
('(63, 159)', '110112122'),
('(159, 63)', '110101210'),
('(415, 415)', '012111220'),
('(95, 415)', '101020101'),
('(415, 95)', '212012220'),
('(95, 95)', '012100102'),
('(383, 447)', '212011010'),
('(447, 383)', '220120112'),
('(447, 127)', '001122122'),
('(127, 447)', '122010111'),
('(383, 63)', '102012022'),
('(63, 383)', '200212201'),
('(127, 63)', '100020111'),
('(63, 127)', '211101012'),
('(415, 447)', '101210202'),
('(447, 415)', '201012120'),
('(95, 447)', '020101012'),
('(447, 95)', '201222112'),
('(63, 415)', '012022010'),
('(415, 63)', '220120022'),
('(95, 63)', '001022010'),
('(63, 95)', '121020001'),
('(447, 447)', '020102202'),
('(63, 447)', '102200102'),
('(447, 63)', '222200111'),
('(63, 63)', '010212200')
]

base_mire_90 = [
    ('(256, 255)', '110201212'),
('(256, 287)', '120021122'),
('(288, 255)', '121112010'),
('(224, 255)', '200120111'),
('(256, 223)', '112020221'),
('(224, 287)', '002012112'),
('(288, 287)', '222111101'),
('(224, 223)', '021212011'),
('(288, 223)', '211102101'),
('(256, 319)', '202001221'),
('(320, 255)', '102120020'),
('(192, 255)', '102212020'),
('(256, 191)', '010211022'),
('(224, 319)', '022200120'),
('(288, 319)', '210212012'),
('(320, 287)', '012211201'),
('(192, 287)', '020221200'),
('(320, 223)', '011221102'),
('(192, 223)', '212111202'),
('(288, 191)', '221010010'),
('(224, 191)', '202111101'),
('(320, 319)', '121220011'),
('(192, 319)', '222020002'),
('(320, 191)', '102200210'),
('(192, 191)', '121101120'),
('(256, 351)', '011202210'),
('(352, 255)', '200100120'),
('(160, 255)', '222121210'),
('(256, 159)', '102102102'),
('(288, 351)', '101022120'),
('(224, 351)', '212220201'),
('(352, 287)', '011012200'),
('(160, 287)', '202212102'),
('(352, 223)', '021011212'),
('(160, 223)', '121211121'),
('(288, 159)', '020121201'),
('(224, 159)', '121110210'),
('(320, 351)', '200121112'),
('(192, 351)', '221202021'),
('(160, 319)', '021222022'),
('(352, 319)', '112100000'),
('(352, 191)', '100102221'),
('(160, 191)', '112120112'),
('(320, 159)', '012012121'),
('(192, 159)', '111001012'),
('(256, 383)', '100120101'),
('(128, 255)', '120002122'),
('(384, 255)', '200201002'),
('(256, 127)', '211000110'),
('(288, 383)', '010101200'),
('(224, 383)', '101222010'),
('(384, 287)', '001022022'),
('(128, 287)', '222001220'),
('(384, 223)', '122012000'),
('(128, 223)', '210021112'),
('(224, 127)', '011120021'),
('(288, 127)', '101201220'),
('(352, 351)', '120211002'),
('(160, 351)', '211120222'),
('(160, 159)', '011210111'),
('(352, 159)', '211021222'),
('(320, 383)', '001012121'),
('(192, 383)', '212122210'),
('(384, 319)', '001100222'),
('(128, 319)', '211202202'),
('(128, 191)', '120212011'),
('(384, 191)', '210122100'),
('(192, 127)', '110022001'),
('(320, 127)', '200112212'),
('(256, 415)', '012011011'),
('(160, 383)', '121112221'),
('(352, 383)', '210021021'),
('(384, 351)', '022110220'),
('(128, 351)', '111122021'),
('(416, 255)', '020210011'),
('(96, 255)', '000110212'),
('(384, 159)', '221212010'),
('(128, 159)', '212101001'),
('(160, 127)', '002102211'),
('(352, 127)', '120222122'),
('(256, 95)', '020010211'),
('(224, 415)', '022121101'),
('(288, 415)', '111010001'),
('(96, 287)', '021010122'),
('(416, 287)', '220020112'),
('(416, 223)', '002120101'),
('(96, 223)', '001122121'),
('(224, 95)', '001221002'),
('(288, 95)', '112002122'),
('(320, 415)', '011100210'),
('(192, 415)', '120212102'),
('(416, 319)', '220002120'),
('(96, 319)', '210100221'),
('(416, 191)', '001221110'),
('(96, 191)', '201211212'),
('(320, 95)', '221121121'),
('(192, 95)', '210222100'),
('(128, 383)', '110111212'),
('(384, 383)', '211210202'),
('(128, 127)', '121010200'),
('(384, 127)', '222121001'),
('(352, 415)', '101002210'),
('(160, 415)', '202111212'),
('(96, 351)', '112012211'),
('(416, 351)', '202002201'),
('(416, 159)', '102220111'),
('(96, 159)', '122110121'),
('(352, 95)', '212211212'),
('(160, 95)', '201022221'),
('(256, 447)', '111200110'),
('(448, 255)', '112000102'),
('(64, 255)', '101211000'),
('(256, 63)', '000121021'),
('(288, 447)', '101101010'),
('(224, 447)', '210210011'),
('(64, 287)', '011121002'),
('(448, 287)', '122201022'),
('(448, 223)', '010001210'),
('(64, 223)', '112102200'),
('(224, 63)', '102222100'),
('(288, 63)', '210010012'),
('(320, 447)', '100110102'),
('(192, 447)', '201021021'),
('(64, 319)', '102110021'),
('(448, 319)', '202221221'),
('(448, 191)', '100011121'),
('(64, 191)', '211011120'),
('(320, 63)', '121200112'),
('(192, 63)', '222212210'),
('(384, 415)', '100122022'),
('(128, 415)', '122011120'),
('(416, 383)', '021202012'),
('(96, 383)', '101201111'),
('(416, 127)', '012210011'),
('(96, 127)', '011101012'),
('(128, 95)', '010102220'),
('(384, 95)', '121212100'),
('(352, 447)', '020101102'),
('(160, 447)', '011212120'),
('(448, 351)', '010222212'),
('(64, 351)', '021211211'),
('(448, 159)', '110101012'),
('(64, 159)', '120121012'),
('(352, 63)', '122101121'),
('(160, 63)', '220221222'),
('(96, 415)', '020121112'),
('(416, 415)', '220120122'),
('(416, 95)', '002121001'),
('(96, 95)', '101010201'),
('(384, 447)', '022011221'),
('(128, 447)', '212201201'),
('(448, 383)', '122020120'),
('(64, 383)', '210120110'),
('(448, 127)', '111000201'),
('(64, 127)', '111220101'),
('(384, 63)', '212111010'),
('(128, 63)', '201002122'),
('(416, 447)', '212012221'),
('(96, 447)', '220010121'),
('(64, 415)', '102012102'),
('(448, 415)', '222201200'),
('(448, 95)', '010010220'),
('(64, 95)', '012201010'),
('(96, 63)', '010120220'),
('(416, 63)', '101210200'),
('(64, 447)', '002201022'),
('(448, 447)', '211222001'),
('(448, 63)', '000102122'),
('(64, 63)', '102022001')
]

base_mire_180 = [
    ('(256, 256)', '112102012'),
('(256, 288)', '110211120'),
('(288, 256)', '121120202'),
('(224, 256)', '122200211'),
('(256, 224)', '211001201'),
('(288, 224)', '011212120'),
('(224, 224)', '012020121'),
('(288, 288)', '201111021'),
('(224, 288)', '201221111'),
('(320, 256)', '022102110'),
('(256, 320)', '120021200'),
('(256, 192)', '120022120'),
('(192, 256)', '221020012'),
('(288, 320)', '002112211'),
('(224, 320)', '001122112'),
('(192, 224)', '020222001'),
('(224, 192)', '000202212'),
('(320, 288)', '210210100'),
('(192, 288)', '212102120'),
('(320, 224)', '201021111'),
('(288, 192)', '202121112'),
('(320, 320)', '110022002'),
('(192, 320)', '111212200'),
('(320, 192)', '120211011'),
('(192, 192)', '202220200'),
('(160, 256)', '010112022'),
('(352, 256)', '102021021'),
('(256, 352)', '220001001'),
('(256, 160)', '210221212'),
('(288, 352)', '012210112'),
('(224, 352)', '000110122'),
('(352, 288)', '001201212'),
('(160, 288)', '120010221'),
('(352, 224)', '110211102'),
('(288, 160)', '121212111'),
('(160, 224)', '201122202'),
('(224, 160)', '202022121'),
('(352, 320)', '021120121'),
('(192, 160)', '022212220'),
('(320, 352)', '121001022'),
('(192, 352)', '100121000'),
('(352, 192)', '112110010'),
('(320, 160)', '112121201'),
('(160, 320)', '212001211'),
('(160, 192)', '221212020'),
('(128, 256)', '101001201'),
('(256, 128)', '122200021'),
('(256, 384)', '202002010'),
('(384, 256)', '210110001'),
('(224, 384)', '022010220'),
('(128, 288)', '000101012'),
('(384, 224)', '021111200'),
('(288, 384)', '100220120'),
('(384, 288)', '120012012'),
('(128, 224)', '110012220'),
('(288, 128)', '212100211'),
('(224, 128)', '220220012'),
('(352, 160)', '011112101'),
('(160, 352)', '102202110'),
('(352, 352)', '222110212'),
('(160, 160)', '222111202'),
('(192, 384)', '022011002'),
('(128, 320)', '021010121'),
('(384, 192)', '101100220'),
('(320, 128)', '111202120'),
('(320, 384)', '200101221'),
('(384, 320)', '212001122'),
('(128, 192)', '210121222'),
('(192, 128)', '202112022'),
('(256, 416)', '011202100'),
('(160, 384)', '020221102'),
('(416, 256)', '011200102'),
('(96, 256)', '011120110'),
('(384, 160)', '011021022'),
('(256, 96)', '012001102'),
('(384, 352)', '122202221'),
('(128, 160)', '121211122'),
('(160, 128)', '121111220'),
('(352, 384)', '210212120'),
('(128, 352)', '221100210'),
('(352, 128)', '201121010'),
('(288, 416)', '001021201'),
('(416, 224)', '002012210'),
('(96, 224)', '001221211'),
('(288, 96)', '021011221'),
('(224, 96)', '022210101'),
('(416, 288)', '122120021'),
('(96, 288)', '101110100'),
('(224, 416)', '212200201'),
('(320, 416)', '010012211'),
('(96, 320)', '010111002'),
('(96, 192)', '102202121'),
('(192, 416)', '220200021'),
('(416, 320)', '221211211'),
('(416, 192)', '200102221'),
('(320, 96)', '212012112'),
('(192, 96)', '221101002'),
('(384, 128)', '100210102'),
('(128, 128)', '112101112'),
('(384, 384)', '201221210'),
('(128, 384)', '202112102'),
('(352, 416)', '111022201'),
('(96, 352)', '110010022'),
('(352, 96)', '121221101'),
('(160, 96)', '111120122'),
('(160, 416)', '201020022'),
('(416, 352)', '212122112'),
('(416, 160)', '221010222'),
('(96, 160)', '212021112'),
('(448, 256)', '021001210'),
('(256, 448)', '102120001'),
('(64, 256)', '110112001'),
('(256, 64)', '100012110'),
('(288, 448)', '010100012'),
('(224, 64)', '002111210'),
('(224, 448)', '122222010'),
('(64, 288)', '110011010'),
('(448, 224)', '100022221'),
('(288, 64)', '100121022'),
('(448, 288)', '212100100'),
('(64, 224)', '211102100'),
('(320, 448)', '121000111'),
('(448, 320)', '112212001'),
('(64, 320)', '102001101'),
('(192, 64)', '121021100'),
('(192, 448)', '221022212'),
('(448, 192)', '210222122'),
('(64, 192)', '221010210'),
('(320, 64)', '220110111'),
('(384, 416)', '011122100'),
('(128, 416)', '012212020'),
('(416, 128)', '020101022'),
('(384, 96)', '012111010'),
('(416, 384)', '100212121'),
('(96, 384)', '122001220'),
('(96, 128)', '120220111'),
('(128, 96)', '111012011'),
('(160, 448)', '012102222'),
('(64, 352)', '002201011'),
('(64, 160)', '020112121'),
('(160, 64)', '011212112'),
('(352, 448)', '112101010'),
('(448, 352)', '121221011'),
('(352, 64)', '112201210'),
('(448, 160)', '222202212'),
('(416, 416)', '001021210'),
('(96, 96)', '012201211'),
('(416, 96)', '101010102'),
('(96, 416)', '222201201'),
('(64, 384)', '021220112'),
('(384, 448)', '101110002'),
('(128, 448)', '120220201'),
('(384, 64)', '101112201'),
('(448, 384)', '210121110'),
('(448, 128)', '222010021'),
('(64, 128)', '201122012'),
('(128, 64)', '210101201'),
('(416, 448)', '020100102'),
('(448, 96)', '020101202'),
('(416, 64)', '010122010'),
('(448, 416)', '100012102'),
('(96, 64)', '102020121'),
('(96, 448)', '200222012'),
('(64, 416)', '221120122'),
('(64, 96)', '221200101'),
('(448, 448)', '022001021'),
('(64, 64)', '022022010'),
('(448, 64)', '101020220'),
('(64, 448)', '201112220')
]

base_mire_270 = [
('(255, 256)', '112121020'),
('(287, 256)', '201110012'),
('(255, 288)', '102211202'),
('(255, 224)', '111222002'),
('(223, 256)', '120102111'),
('(287, 288)', '020112121'),
('(287, 224)', '021120201'),
('(223, 288)', '221011110'),
('(223, 224)', '211012211'),
('(319, 256)', '120200221'),
('(255, 320)', '010221021'),
('(255, 192)', '212210200'),
('(191, 256)', '100200212'),
('(319, 224)', '012002022'),
('(319, 288)', '212021211'),
('(287, 192)', '001202220'),
('(287, 320)', '211010211'),
('(223, 320)', '200102101'),
('(223, 192)', '220121021'),
('(191, 288)', '011021122'),
('(191, 224)', '012011221'),
('(319, 320)', '111202110'),
('(319, 192)', '200022202'),
('(191, 320)', '102100220'),
('(191, 192)', '100112122'),
('(351, 256)', '212102212'),
('(255, 160)', '022101120'),
('(255, 352)', '121020210'),
('(159, 256)', '201200010'),
('(351, 288)', '111212121'),
('(351, 224)', '221020221'),
('(287, 352)', '102102111'),
('(287, 160)', '202011222'),
('(223, 352)', '012012012'),
('(223, 160)', '121200102'),
('(159, 288)', '012122101'),
('(159, 224)', '022001101'),
('(351, 192)', '020222122'),
('(351, 320)', '101121212'),
('(319, 352)', '110121100'),
('(319, 160)', '220212120'),
('(191, 352)', '021211201'),
('(191, 160)', '211120012'),
('(159, 320)', '122210010'),
('(159, 192)', '100001210'),
('(383, 256)', '121222000'),
('(255, 128)', '101010012'),
('(255, 384)', '201101100'),
('(127, 256)', '210020020'),
('(383, 288)', '211121002'),
('(383, 224)', '212202200'),
('(287, 384)', '000211112'),
('(287, 128)', '120100122'),
('(223, 128)', '012001010'),
('(223, 384)', '112200120'),
('(127, 224)', '020220102'),
('(127, 288)', '120002201'),
('(351, 352)', '001111121'),
('(351, 160)', '202221112'),
('(159, 160)', '110022021'),
('(159, 352)', '212221102'),
('(383, 320)', '120112021'),
('(383, 192)', '222021120'),
('(319, 384)', '120011002'),
('(319, 128)', '222101212'),
('(191, 128)', '021210101'),
('(191, 384)', '222120011'),
('(127, 192)', '002220110'),
('(127, 320)', '221001012'),
('(415, 256)', '002120011'),
('(383, 160)', '120211112'),
('(383, 352)', '210011210'),
('(351, 384)', '022110210'),
('(351, 128)', '122212111'),
('(255, 416)', '002112001'),
('(255, 96)', '010111201'),
('(159, 384)', '121222022'),
('(159, 128)', '210211002'),
('(127, 160)', '002202211'),
('(127, 352)', '220102121'),
('(95, 256)', '000112021'),
('(415, 288)', '021210112'),
('(415, 224)', '001222101'),
('(287, 416)', '010020122'),
('(287, 96)', '011012212'),
('(223, 416)', '121221200'),
('(223, 96)', '100011101'),
('(95, 288)', '001010212'),
('(95, 224)', '201122002'),
('(415, 320)', '212120121'),
('(415, 192)', '202211010'),
('(319, 96)', '121022021'),
('(319, 416)', '221001022'),
('(191, 96)', '002101110'),
('(191, 416)', '211212112'),
('(95, 320)', '011100122'),
('(95, 192)', '221202000'),
('(383, 384)', '102002101'),
('(383, 128)', '112121011'),
('(127, 384)', '210012212'),
('(127, 128)', '202021121'),
('(415, 352)', '101212211'),
('(415, 160)', '122111201'),
('(351, 416)', '222210102'),
('(351, 96)', '212120211'),
('(159, 96)', '122100100'),
('(159, 416)', '212121221'),
('(95, 352)', '101110222'),
('(95, 160)', '222010200'),
('(447, 256)', '110000121'),
('(255, 448)', '010210012'),
('(255, 64)', '101101120'),
('(63, 256)', '101021200'),
('(447, 224)', '010021112'),
('(447, 288)', '122001210'),
('(287, 448)', '121000222'),
('(287, 64)', '200111021'),
('(223, 64)', '110100110'),
('(223, 448)', '200121001'),
('(63, 288)', '012101000'),
('(63, 224)', '110222220'),
('(447, 192)', '100210211'),
('(447, 320)', '211201101'),
('(319, 448)', '222102221'),
('(319, 64)', '210210102'),
('(191, 448)', '101122120'),
('(191, 64)', '101020011'),
('(63, 320)', '111210001'),
('(63, 192)', '212210222'),
('(415, 384)', '010121110'),
('(415, 128)', '111110120'),
('(383, 416)', '022201010'),
('(383, 96)', '111202201'),
('(127, 416)', '121002121'),
('(127, 96)', '120220012'),
('(95, 384)', '000111221'),
('(95, 128)', '020122120'),
('(447, 160)', '012112121'),
('(447, 352)', '110122012'),
('(351, 64)', '021201121'),
('(351, 448)', '212222022'),
('(159, 64)', '011022010'),
('(159, 448)', '111212210'),
('(63, 160)', '022121022'),
('(63, 352)', '110121010'),
('(415, 96)', '011122012'),
('(415, 416)', '102010101'),
('(95, 416)', '010010212'),
('(95, 96)', '201222012'),
('(447, 384)', '101011122'),
('(447, 128)', '201101012'),
('(383, 448)', '221220100'),
('(383, 64)', '212011220'),
('(127, 64)', '012212201'),
('(127, 448)', '210101211'),
('(63, 384)', '102011100'),
('(63, 128)', '101202202'),
('(447, 416)', '010101220'),
('(447, 96)', '121020201'),
('(415, 448)', '002201012'),
('(415, 64)', '201212001'),
('(95, 448)', '102000121'),
('(95, 64)', '222211201'),
('(63, 416)', '002201001'),
('(63, 96)', '212002220'),
('(447, 64)', '010220220'),
('(447, 448)', '120010202'),
('(63, 448)', '021220010'),
('(63, 64)', '220011122')
]


# --- Fin de tes listes base_mire_X ---


# Liste contenant toutes les bases de mires pour la recherche de l'orientation
all_base_mires = [
    ("0 degrés", base_mire_0),
    ("90 degrés", base_mire_90),
    ("180 degrés", base_mire_180),
    ("270 degrés", base_mire_270)
]

# --- Dictionnaire lookup pour base_mire_0 (pour la correction FINALE) ---
# On le crée juste pour avoir les coordonnées de base_mire_0 si nécessaire pour la correction,
# bien que dans cette approche, on n'aligne pas DIRECTEMENT sur ces points.
# C'est la MÊME lookup que dans la version précédente.
base_mire_0_lookup = {}
for coords_str, code in base_mire_0:
    try:
        x_str, y_str = coords_str.strip('()').split(', ')
        base_mire_0_lookup[code] = (int(x_str), int(y_str))
    except ValueError:
        print(f"Erreur de parsing pour les coordonnées originales dans base_mire_0: {coords_str}")
        continue # Skip this entry


# === CHARGER IMAGES ===
img_original = cv.imread(image_original_path)
img_transformed = cv.imread(image_transformed_path)

if img_original is None:
    print(f"Erreur de chargement de l'image originale: {image_original_path}")
    exit()
if img_transformed is None:
    print(f"Erreur de chargement de l'image transformée: {image_transformed_path}")
    exit()


# === DÉTECTER MOTIFS TRANSFORMÉS ===
print("Détection des motifs dans l'image transformée...")
code2.center_tab = [] # Réinitialise center_tab avant chaque détection
code2.transformed_mire = img_transformed # Définit l'image à traiter dans code2
code2.fullContoursProcess(code2.transformed_mire) # Exécute la détection
center_tab_transformed = code2.center_tab.copy() # Copie les résultats

print(f"Détecté {len(center_tab_transformed)} motifs dans l'image transformée.")

if not center_tab_transformed:
    print("Aucun motif détecté dans l'image transformée.")
    exit()

# === ANGLE DE DÉPART ===
# Utilisé pour orienter la recherche des voisins (directions 0-7) par rapport à la rotation globale de la mire.
# code2.angleRedPattern doit détecter le motif rouge et retourner son angle (par exemple, 0 pour Est, 90 pour Sud, etc.)
starting_angle = code2.angleRedPattern(img_transformed)
print(f"Angle de départ (basé sur motif rouge): {starting_angle}°")


# === RECHERCHE VOISINS ===
# Identique à la version précédente
def find_neighbor(center_tab, cx, cy, angle, init_dist, step_size, max_dist):
    angle_rad = math.radians(angle)
    d = init_dist
    while d <= max_dist:
        approx_x = cx + d * math.cos(angle_rad)
        approx_y = cy + d * math.sin(angle_rad)
        for (x, y, motif_type) in center_tab:
            if (x, y) == (cx, cy):
                continue
            distance_to_approx_pos = math.hypot(x - approx_x, y - approx_y)
            if distance_to_approx_pos < step_size:
                actual_distance = math.hypot(x - cx, y - cy)
                return motif_type, (x, y), actual_distance
        d += step_size
    return "N", None, None # Not found


# === PROCESS MOTIF ===
# Identique à la version précédente
def process_motif(center_tab, index, start_angle):
    if index is None or index < 0 or index >= len(center_tab):
        return None
    motif_x, motif_y, motif_type = center_tab[index]
    neighbor_types = []
    for i in range(8):
        angle = (i * 45 + start_angle) % 360
        neighbor_type, neighbor_coords, dist = find_neighbor(
            center_tab, motif_x, motif_y, angle,
            distance_init, step_size, max_distance
        )
        neighbor_types.append(str(neighbor_type))
    neighbor_code = str(motif_type) + "".join(neighbor_types)
    return (f"({int(motif_x)}, {int(motif_y)})", neighbor_code)


# === PROCESS ALL DETECTED MOTIFS ===
# Génère les codes de voisinage pour tous les motifs détectés dans l'image transformée.
motifs_data = []  # Liste pour stocker les résultats (coordonnées transformées et codes)

print(f"\nProcessing {len(center_tab_transformed)} detected motifs to generate codes...")

for index in range(len(center_tab_transformed)):
    motif_data = process_motif(center_tab_transformed, index, starting_angle)
    if motif_data:
        motifs_data.append(motif_data)

print(f"Finished processing motifs. Generated codes for {len(motifs_data)} points.")


# ==========================================================
# === CALCULER LA TRANSFORMATION EN 2 ÉTAPES ===
# ==========================================================

print("\n--- Début de la recherche de transformation en 2 étapes ---")

# 1. Trouver la meilleure mire de référence (pour l'orientation de l'ENTREE)
best_match_count = 0
best_match_base_mire_name = None
best_match_base_mire_list = None # On stocke la liste entière de la meilleure mire
best_match_original_lookup = None # Dictionnaire lookup pour la meilleure mire

print("Recherche de la meilleure orientation de la mire de référence (pour identifier l'entrée)...")

for mire_name, base_mire_list in all_base_mires:
    current_original_lookup = {}
    for coords_str, code in base_mire_list:
        try:
            x_str, y_str = coords_str.strip('()').split(', ')
            current_original_lookup[code] = (int(x_str), int(y_str))
        except ValueError:
            continue
    current_match_count = 0
    for _, transformed_code in motifs_data:
        if transformed_code in current_original_lookup:
            current_match_count += 1

    # print(f"  Correspondances trouvées pour {mire_name} : {current_match_count}")

    if current_match_count > best_match_count:
        best_match_count = current_match_count
        best_match_base_mire_name = mire_name
        best_match_base_mire_list = base_mire_list # Stocke la liste
        best_match_original_lookup = current_original_lookup # Stocke le lookup

if best_match_count < 4:
    print(f"\nErreur: Seulement {best_match_count} correspondances trouvées avec la meilleure mire ({best_match_base_mire_name}). Nécessite au moins 4 points pour calculer une transformation.")
    exit()
else:
    print(f"\nMeilleure mire de référence trouvée (pour l'entrée): {best_match_base_mire_name} avec {best_match_count} correspondances.")


# 2. Collecter les paires de points (Source -> Cible Temporaire)
# La SOURCE sont les points détectés dans l'image transformée.
# La CIBLE TEMPORAIRE sont les points correspondants dans la *meilleure mire trouvée*.

points_transformed_list = [] # Liste de tuples (xt, yt) des points détectés (Source)
points_best_match_list = []  # Liste de tuples (xo, yo) des points correspondants dans la MEILLEURE MIRE (Cible Temporaire)

print("Collecte des paires de points correspondants (points transformés -> points de la meilleure mire)...")

# On parcourt les motifs détectés dans l'image transformée
for transformed_coords_str, transformed_code in motifs_data:
    # Parser les coordonnées du point détecté
    try:
        xt_str, yt_str = transformed_coords_str.strip('()').split(', ')
        transformed_point = (int(xt_str), int(yt_str))
    except ValueError:
        print(f"Erreur de parsing pour les coordonnées transformées : {transformed_coords_str}")
        continue

    # Chercher le code détecté dans le dictionnaire de la *meilleure* mire trouvée
    if transformed_code in best_match_original_lookup:
        # Si le code est trouvé, le point cible TEMPORAIRE est celui de la meilleure mire
        best_match_point = best_match_original_lookup[transformed_code]

        # Ajouter la paire : point détecté (source) et point dans la meilleure mire (cible TEMPORAIRE)
        points_transformed_list.append(transformed_point)
        points_best_match_list.append(best_match_point)
        # print(f"  Paire temporaire : Transformed {transformed_point} -> Best Match {best_match_point} (Code: {transformed_code})")
    # else:
        # Ce code détecté n'est pas un code valide dans la meilleure mire
        # print(f"  Code {transformed_code} détecté n'a pas de correspondance dans la meilleure mire.")


# Convertir les listes en numpy arrays de type float32
points_transformed_np = np.array(points_transformed_list, dtype=np.float32)
points_best_match_np = np.array(points_best_match_list, dtype=np.float32) # Points dans la meilleure mire

print(f"Collecté {len(points_transformed_np)} paires de points valides (transformés -> meilleure mire) pour le calcul de la première matrice.")

# 3. Calculer la première matrice: Transfomation de l'image transformée vers la meilleure mire.
M_to_best_match = None # Matrice de transformation de l'image transformée vers la meilleure mire

if len(points_transformed_np) < 4:
    print("Erreur: Pas assez de points collectés pour M_to_best_match.")
else:
    if len(points_transformed_np) > 4:
        print("Calcul de M_to_best_match (Homographie) avec RANSAC...")
        M_to_best_match, mask = cv.findHomography(points_transformed_np, points_best_match_np, cv.RANSAC, 5.0)
        if M_to_best_match is not None:
             print(f"M_to_best_match calculée (avec {np.sum(mask)} inliers).")
        else:
             print("cv.findHomography pour M_to_best_match a échoué.")
    else: # Exactement 4 points
        print("Calcul de M_to_best_match avec exactement 4 points...")
        M_to_best_match = cv.getPerspectiveTransform(points_transformed_np, points_best_match_np)
        print("M_to_best_match calculée.")

    if M_to_best_match is not None:
        print(M_to_best_match)
    else:
         print("Le calcul de M_to_best_match a échoué.")


# 4. Calculer la deuxième matrice: Rotation pour aller de la meilleure mire à base_mire_0.
M_correction_rotation = None # Matrice de correction de rotation

if M_to_best_match is not None:
    correction_angle = 0 # Angle de rotation nécessaire pour aller de la meilleure mire à 0 degrés
    if best_match_base_mire_name == "90 degrés":
        correction_angle = 90 # Pour aller de 90 à 0, on tourne de -90 (ou 270)
    elif best_match_base_mire_name == "180 degrés":
        correction_angle = 180 # Pour aller de 180 à 0, on tourne de -180 (ou 180)
    elif best_match_base_mire_name == "270 degrés":
        correction_angle = 270 # Pour aller de 270 à 0, on tourne de -270 (ou 90)

    # Déterminer le centre de rotation. Utilisons le centre de l'image de la mire originale (base_mire_0).
    # Un centre commun approx est (256, 256) ou (255, 255). Prenons (256, 256) pour simplifier.
    center_of_rotation = (img_original.shape[1] // 2, img_original.shape[0] // 2) # Centre de l'image de sortie

    print(f"\nCalcul de la matrice de correction de rotation (-{correction_angle} degrés) autour de {center_of_rotation}...")

    # cv.getRotationMatrix2D donne une matrice 2x3 pour rotation 2D affine
    M_rotation_affine = cv.getRotationMatrix2D(center_of_rotation, correction_angle, 1.0)

    # Convertir la matrice affine 2x3 en matrice 3x3 projective pour pouvoir la multiplier avec une homographie
    M_correction_rotation = np.vstack([M_rotation_affine, [0, 0, 1]]).astype(np.float32)

    print("Matrice de correction de rotation calculée:")
    print(M_correction_rotation)

# 5. Composer les deux matrices: M_final = M_correction_rotation * M_to_best_match
# L'ordre de multiplication est important : on applique d'abord M_to_best_match, puis M_correction_rotation.
M_final = None
if M_to_best_match is not None and M_correction_rotation is not None:
    print("\nComposition des matrices: M_final = M_correction_rotation @ M_to_best_match")
    M_final = M_correction_rotation @ M_to_best_match # Utilise l'opérateur @ pour la multiplication matricielle

    print("Matrice de transformation finale calculée:")
    print(M_final)
else:
    print("\nImpossible de calculer la matrice finale (une des matrices intermédiaires manquait).")


# 6. Appliquer la Transformation Finale
img_aligned = None # Initialise l'image alignée à None

if M_final is not None:
    # L'image de sortie doit avoir la même taille que l'image originale (base_mire_0)
    output_width, output_height = img_original.shape[1], img_original.shape[0]
    output_size = (output_width, output_height) # cv.warpPerspective attend (width, height)

    print(f"\nApplication de la transformation finale à l'image transformée (taille de sortie: {output_size})...")
    img_aligned = cv.warpPerspective(img_transformed, M_final, output_size)

else:
    print("\nLa matrice de transformation finale n'a pas pu être calculée. L'alignement ne sera pas effectué.")


# ==========================================================
# === AFFICHAGE DES RESULTATS ===
# ==========================================================

# 7. Afficher les images pour visualiser le résultat de l'alignement
print("\nAffichage des images : Originale, Transformée d'origine, et Transformée Alignée (vers l'Originale).")

# Affiche l'image originale (la cible)
cv.imshow("Image Originale (Cible de l'alignement)", img_original)

# Affiche l'image transformée telle qu'elle a été chargée initialement
cv.imshow("Image Transformee (Originale chargee)", img_transformed)

# Affiche l'image alignée seulement si le calcul et l'application ont réussi
if img_aligned is not None:
     cv.imshow("Image Transformee Alignee (vers Originale)", img_aligned)

print("Appuyez sur n'importe quelle touche pour fermer les fenêtres d'affichage.")
cv.waitKey(0) # Attend une pression de touche dans une fenêtre OpenCV
cv.destroyAllWindows() # Ferme toutes les fenêtres OpenCV ouvertes

# Optionnel: Sauvegarder l'image alignée sur le disque
if img_aligned is not None:
   cv.imwrite("aligned_to_original_mire_2step.png", img_aligned)
   print("Image alignée sauvegardée sous 'aligned_to_original_mire_2step.png'")