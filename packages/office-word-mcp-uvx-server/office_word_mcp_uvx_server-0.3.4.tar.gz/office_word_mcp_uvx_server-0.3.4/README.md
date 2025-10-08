### 项目说明
- 模型上下文协议（MCP）服务器，允许您在无需安装Microsoft Word 的情况下操作 Word 文件。使用您的AI代理创建、阅读和修改 Word 工作簿。
- 项目名称：office-word-mcp-uvx-server
- 当前版本号：0.2.6
- 项目重度参考了 https://github.com/GongRzhe/Office-Word-MCP-Server 感谢原作者，但是修改了大量的bug
- pipy url: https://pypi.org/project/office-word-mcp-uvx-server/

### 技术参数
- python 3.11
- 框架使用 FastMCP
- 操作文件必须使用绝对路径，保证文件操作的准确性。

### 目录说明
- test/ 测试目录 python 用 unittest 写单元测试，文件格式 test_<测试功能>.py
  - 测试用 docx 文件：test/office_files/模版/QN-QR-24-01-003 进料检验单（结构件）.docx
- src/ 源代码目录
  - 下面的文件是一个功能对应一个 py 文件
- demo/ 示例代码目录
- pyproject.toml 项目配置文件
- VERSION 版本号文件
- build_and_publish_uv.sh 打包命令

### 功能
- [x] **`get_paragraph_text_from_document`**: 【已实现】从 Word 文档的特定段落获取文本。
- [x] **`find_text_in_document`**: 【已实现】在 Word 文档中查找特定文本的出现。
- [x] **`get_document_xml`**: 获取 Word 文档的原始 XML 结构。
- [x] **`search_and_replace`**: 【已实现】搜索文本并替换所有出现的地方。
- [x] **`create_document`**: 【已实现】创建一个带有可选元数据的新 Word 文档。
- [x] **`get_document_info`**: 【已实现】获取有关 Word 文档的信息。
- [x] **`get_document_text`**: 【已实现】从 Word 文档中提取所有文本。
- [x] **`get_document_outline`**: 【已实现】获取 Word 文档的结构。
- [x] **`insert_header_near_text`**: 【已实现】在包含目标文本的第一个段落之前或之后插入页眉（使用指定样式）。
- [x] **`insert_line_or_paragraph_near_text`**: 【已实现】在包含的第一个段落之前或之后插入一个新行或段落（使用指定或匹配的样式）。
- [x] **`add_paragraph`**: 【已实现】向 Word 文档中添加一个段落。
- [x] **`add_heading`**: 【已实现】向 Word 文档中添加一个标题。
- [x] **`add_picture`**: 【已实现】向 Word 文档中添加一张图片。
- [x] **`add_table`**: 【已实现】向 Word 文档中添加一个表格。
- [x] **`add_page_break`**: 【已实现】向文档中添加一个分页符。
- [x] **`delete_paragraph`**: 【已实现】从文档中删除一个段落。
- [x] **`create_custom_style`**: 【已实现】在文档中创建一个自定义样式。
- [x] **`format_text`**: 【已实现】在段落内格式化特定范围的文本。
- [x] **`format_table`**: 【已实现】使用边框、底纹和结构格式化表格。
- [x] **`protect_document`**: 【已实现】为 Word 文档添加密码保护（无 msoffcrypto 实现，和 office 加密有所区别）。
- [x] **`unprotect_document`**: 【已实现】从 Word 文档中删除密码保护。
- [x] **`add_footnote_to_document`**: 【已实现】向 Word 文档的特定段落添加脚注。
- [x] **`add_endnote_to_document`**: 【已实现】向 Word 文档的特定段落添加尾注。
- [x] **`customize_footnote_style`**: 【已实现】自定义脚注编号和格式。

- ~~**`convert_to_pdf`**: 【不制作，直接用打印到pdf 功能最还原】将 Word 文档转换为 PDF 格式。~~
- ~~**`copy_document`**: 【不制作，直接用shell cp 就行了】创建一个 Word 文档的副本。~~
- ~~**`list_available_documents`**: 列出指定目录中的所有 .docx 文件。~~
### 使用方法
```bash
uvx --index-url=https://nexus3.m.6do.me:4000/repository/pypi-group/simple --from office-word-mcp-uvx-server word-mcp-server --help
```

```json
{
  "mcpServers": {
    "word-mcp-nexus": {
      "command": "uvx",
      "args": [
        "--index-url",
        "https://nexus3.m.6do.me:4000/repository/pypi-group/simple",
        "--from",
        "office-word-mcp-uvx-server==0.3.4",
        "word-mcp-server",
        "stdio"
      ]
    }
  }
}
```