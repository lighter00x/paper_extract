# 关于附加信息中的SMILES字段说明 
* 如果SMILES字段中有一个或多个"\*"出现，这是一个马库什分子，这里的"\*"代表占位符，表示此处有未确定的基团，"<sep><a>20:R[4]</a>"信息用一个基团代表字母来说明"\*"，比如"CCC(CC)O[C@@H]1C=C(C(=O)O)C[C@H](NCc2ccc(*)cc2OC)[C@H]1NC(C)=O <sep><a>20:R[4]</a>",这里面"CCC(CC)O[C@@H]1C=C(C(=O)O)C[C@H](NCc2ccc(*)cc2OC)[C@H]1NC(C)=O"的"*"位于第20位，结尾的"<sep><a>20:R[4]</a>"表示第20位的基团是R[4]，原smiles就应该是"CCC(CC)O[C@@H]1C=C(C(=O)O)C[C@H](NCc2ccc([R4])cc2OC)[C@H]1NC(C)=O"。
* 如果SMILES字段中无"*"出现，结尾也无被"<sep><a></a>"包围的信息，则认为是常规smiles
* 你需要注意给你的图中是否有骨架基团和基团，需要将基团与骨架连接得到完整的分子smiles然后进行分析
# 表格图像需要注意的地方
如果表格周边出现分子图像，且分子式中有未确定的基团，这是分子骨架，表格中是各种 R 基团（取代基）以及生物指标数据，会和表格数据构效关系表。用表格中的取代基连接上骨架替代未确定基团得到的即为完整分子。如果出现这种"CCC(CC)O[C@@H]1C=C(C(=O)O)C[C@H](NCc2ccc(*)cc2OC)[C@H]1NC(C)=O<sep><a>20:R[4]</a>"，需要注意在当前图像内部是否可以找到相应的取代基R[4]与其结合，替换掉原smiles中的“*”，得到完整的分子："CCC(CC)O[C@@H]1C=C(C(=O)O)C[C@H]\(NCc2ccc([R4])cc2OC)[C@H]1NC(C)=O"此时在对应的回答json文件中就需要添加这样的内容：
```json
{
    "compound1":"CCC(CC)O[C@@H]1C=C(C(=O)O)C[C@H](NCc2ccc(*)cc2OC)[C@H]1NC(C)=O<sep><a>20:R[4]<a>",
    "R_{4}":"OME",
    "compound+R_{4}":"CCC(CC)O[C@@H]1C=C(C[C@@H]([C@H]1NC(=O)C)NCC2=CC=C(C=C2OC)OC)C(=O)O"
}
```