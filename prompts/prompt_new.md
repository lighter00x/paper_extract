请用中文完成以下任务，并严格按照指定格式进行结构化输出。
你将接收的输入信息包括：
- 论文的全文文本信息
- 论文相关图像的理解信息（论文图像解释）
- 论文中含有分子的图像其中个包含的分子的信息（附加信息）
- 关于回答的一点额外说明（附加信息）

请阅读该药学分子研究论文，按照要求提取其中的信息。为你提供的信息有论文文本信息，论文图像理解信息（位于文本信息后）。具体提取信息包括：确定论文的研究分子对象，在该分子的基础上进行了哪些部位的改进，改进后的分子信息什么样，如果有多条改进的路线，在各种改进下，请查阅文献的表格数据，改进后的分子与原分子在哪些指标上有提高，按照以下格式进行输出，如果存在请依照原文进行回答，如果没有也请说明，不要随意编造。特别需要注意，回答时如果涉及到图像相关，请说明文件名，并根据markdown语法规则将涉及的图像的路径附在文字后面,具体的格式在下面，


### 注意事项：
1. **关键指标覆盖**：改进前后的关键指标数据需覆盖全部改进路线，涉及分子部分必须使用SMILES表达式
2. **路线结构化**：按“路线一、路线二···”分点描述，每条路线包含改进前/后信息、改进部位、依据及图像引用
3. **图像引用规范**：插入图像语句需符合Markdown语法，路径格式为`![图像说明](图像路径)`，说明需包含文件名（如Fig.1分子结构示意图）
4. **数据溯源**：所有分子信息需标注在论文中的位置（如：P3右栏第一段/Fig.2A），无SMILES数据时需说明原文指代名称


### 输出格式：
# 1. 论文标题  

# 2. 论文作者  

# 3. 论文研究内容以及主要贡献  

# 4. 分子改进路线叙述  
## 路线一  
### （1）改进前分子信息  
- **位置**：[P2左栏图1/Table1第一行]  
- **分子化学式（smiles）**：[如：C1=CC=C(C=C1)NCOCH3]  
- **分子结构所在图像**：
![改进前分子结构](图像路径)  
- **存在问题**：

### （2）改进部位  
[具体描述，如：在R1位置引入三氟甲基基团，R3位置将酯基替换为酰胺基]  

### （3）改进依据  [根据文献中提到的内容进行查找，理论依据或者实验依据]


### （4）改进后分子信息  
- **位置**：[P4右栏图3/Table2第二行]  
- **分子化学式（smiles）**：[如：C1=CC=C(C=C1)C(F)(F)FNCONHCH3]  
- **分子结构所在图像**：![改进后分子结构](images/图像名.jpg)  

## 路线二  
### （1）改进前分子信息  
- **位置**：[P3中间段落/Fig.2B]  
- **分子化学式（smiles）**：[如：无法获取SMILES，原文称为“化合物3a”]  
- **分子结构所在图像**：
![化合物3a结构](图像路径)  
- **存在问题**：[如：对突变型靶点选择性差（IC50=230nM vs野生型15nM）]  

### （2）改进部位  
[如：在哌啶环4位引入氯原子，苯环2位添加氨基]  

### （3）改进依据[根据文献中提到的内容进行查找，理论依据或者实验依据]

### （4）改进后分子信息  
- **位置**：[P5表3/Fig.4C]  
- **分子化学式（smiles）**：[如：ClC1CN(C)C(Cl)C(C1)NC6H4NH2]  
- **分子结构所在图像**：
![化合物3b结构](图像路径)  
······
（多条改进路线的方案）

# 5. 分子改进后适用于什么疾病  
[如：非小细胞肺癌（针对EGFR T790M突变型）、阿尔茨海默病]  


# 6. 改进前后分子的关键指标数据对比  
| 改进路线 | 改进前分子（SMILES）         | 改进部位（具体基团）       | 改进后分子（SMILES）         | 指标1（IC50/nM） | 指标2（血脑屏障穿透率/%） | 指标3（半衰期/h） |
|----------|-----------------------------|---------------------------|-----------------------------|------------------|---------------------------|-------------------|
| 路线一   | C1=CC=C(C=C1)NCOCH3         | 添加基团R1:[smiles或者分子名称]  | C1=CC=C(C=C1)C(F)(F)FNCONHCH3 | 210→35           | 2→18                      | 1.2→4.5           |
| 路线二   | 化合物3a（无SMILES）         | 哌啶环4-Cl；苯环2-NH2      | ClC1CN(C)C(Cl)C(C1)NC6H4NH2   | 230→18（突变型） | -                         | 1.8→2.1           |


### 使用说明：  
1. 请根据实际论文内容填充各字段，**无相关信息处需明确标注“无”或“未提及”**  
2. 指标名称需与原文一致（如：活性、选择性、毒性等），数据直接对应改进路线  
3. 图像路径需参考论文附录或正文中的图注编号（如：Fig.5A、Supplementary Fig.S2）  
