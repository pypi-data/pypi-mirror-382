# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class FefferyMarkdown(Component):
    """A FefferyMarkdown component.
markdown渲染组件FefferyMarkdown

Keyword arguments:

- id (string; optional):
    组件唯一id.

- key (string; optional):
    对当前组件的`key`值进行更新，可实现强制重绘当前组件的效果.

- children (a list of or a singular dash component, string or number; optional):
    强制渲染呈现的内容，优先级高于`markdownStr`、`placeholder`.

- className (string; optional):
    根容器css类名.

- locale (a value equal to: 'en-us', 'zh-cn'; default 'zh-cn'):
    组件文案语种，可选项有`'zh-cn'`、`'en-us'`  默认值：`'zh-cn'`.

- markdownStr (string; optional):
    markdown字符串.

- placeholder (a list of or a singular dash component, string or number; optional):
    组件型，设置当`markdownStr`为空时的占位内容.

- codeTheme (a value equal to: 'a11y-dark', 'atom-dark', 'coldark-cold', 'coldark-dark', 'coy', 'coy-without-shadows', 'darcula', 'dracula', 'nord', 'okaidia', 'prism', 'solarizedlight', 'twilight', 'duotone-sea', 'duotone-dark', 'duotone-light', 'duotone-space', 'gh-colors', 'gruvbox-dark', 'material-dark', 'night-owl', 'one-light', 'pojoaque', 'solarized-dark-atom', 'synthwave84', 'z-touch'; default 'gh-colors'):
    针对文档中的代码块，设置所应用的代码主题，可选项有`'a11y-dark'`、`'atom-dark'`、`'coldark-cold'`、`'coldark-dark'`、`'coy'`、
    `'coy-without-shadows'`、`'darcula'`、`'dracula'`、`'nord'`、`'okaidia'`、`'prism'`、`'solarizedlight'`、`'twilight'`、
    `'duotone-sea'`、`'duotone-dark'`、`'duotone-light'`、`'duotone-space'`、`'gh-colors'`、`'gruvbox-dark'`、`'material-dark'`、
    `'night-owl'`、`'one-light'`、`'pojoaque'`、`'solarized-dark-atom'`、`'synthwave84'`、`'z-touch'`
    默认值：`'gh-colors'`.

- renderHtml (boolean; optional):
    是否解析渲染`markdownStr`中的html源码  默认值：`False`.

- linkTarget (string; default '_blank'):
    markdown中链接的跳转方式  默认值：`'_blank'`.

- linkTransformFunc (string; optional):
    针对markdown中原始的链接地址，定义用于产生实际链接地址的`javascript`函数字符串.

- codeBlockStyle (dict; optional):
    针对文档中的代码块，设置额外css样式.

- codeStyle (dict; optional):
    针对文档中的代码内容，设置额外css样式.

- showLineNumbers (boolean; default True):
    代码块是否显示行号  默认值：`True`.

- showCopyButton (boolean; default True):
    代码块是否显示右上角复制按钮  默认值：`True`.

- imagePreview (boolean; default False):
    针对文档中的图片，是否添加交互查看功能  默认值：`False`.

- imageFallback (string; optional):
    针对文档中的图片，设置资源加载失败时的占位图资源地址.

- imageForceAlignCenter (boolean; default False):
    针对文档中的图片，是否强制居中显示  默认值：`False`.

- imageWidth (string | number; optional):
    为文档中的所有图片强制设置统一的宽度.

- imageHeight (string | number; optional):
    为文档中的所有图片强制设置统一的高度.

- forceTableAlignCenter (boolean; default False):
    针对文档中的表格，是否强制居中显示  默认值：`True`.

- forceTableHeaderTextAlignCenter (boolean; default True):
    针对文档中的表格，是否强制表头单元格内文字居中  默认值：`True`.

- forceTableContentTextAlignCenter (boolean; default True):
    针对文档中的表格，是否强制普通单元格内文字居中  默认值：`True`.

- h1Style (dict; optional):
    针对文档中的一级标题内容，设置额外css样式.

- h1ClassName (string; optional):
    针对文档中的一级标题内容，设置额外css类名.

- h2Style (dict; optional):
    针对文档中的二级标题内容，设置额外css样式.

- h2ClassName (string; optional):
    针对文档中的二级标题内容，设置额外css类名.

- h3Style (dict; optional):
    针对文档中的三级标题内容，设置额外css样式.

- h3ClassName (string; optional):
    针对文档中的三级标题内容，设置额外css类名.

- h4Style (dict; optional):
    针对文档中的四级标题内容，设置额外css样式.

- h4ClassName (string; optional):
    针对文档中的四级标题内容，设置额外css类名.

- h5Style (dict; optional):
    针对文档中的五级标题内容，设置额外css样式.

- h5ClassName (string; optional):
    针对文档中的五级标题内容，设置额外css类名.

- h6Style (dict; optional):
    针对文档中的六级标题内容，设置额外css样式.

- h6ClassName (string; optional):
    针对文档中的六级标题内容，设置额外css类名.

- tableStyle (dict; optional):
    针对文档中的表格内容，设置额外css样式.

- tableClassName (string; optional):
    针对文档中的表格内容，设置额外css类名.

- theadStyle (dict; optional):
    针对文档中的表格表头内容，设置额外css样式.

- theadClassName (string; optional):
    针对文档中的表格表头内容，设置额外css类名.

- trStyle (string; optional):
    针对文档中的表格数据行内容，设置额外css样式.

- trClassName (string; optional):
    针对文档中的表格数据行内容，设置额外css类名.

- thStyle (dict; optional):
    针对文档中的表格表头单元格内容，设置额外css样式.

- thClassName (string; optional):
    针对文档中的表格表头单元格内容，设置额外css类名.

- tdStyle (string; optional):
    针对文档中的表格数据单元格内容，设置额外css样式.

- tdClassName (string; optional):
    针对文档中的表格数据单元格内容，设置额外css类名.

- aStyle (dict; optional):
    针对文档中的链接内容，设置额外css样式.

- aClassName (string; optional):
    针对文档中的链接内容，设置额外css类名.

- blockquoteStyle (dict; optional):
    针对文档中的引用块内容，设置额外css样式.

- blockquoteClassName (string; optional):
    针对文档中的引用块内容，设置额外css类名.

- inlineCodeStyle (dict; optional):
    针对文档中的行内代码内容，设置额外css样式.

- inlineCodeClassName (string; optional):
    针对文档中的行内代码内容，设置额外css类名.

- hrStyle (dict; optional):
    针对文档中的水平分割线内容，设置额外css样式.

- hrClassName (string; optional):
    针对文档中的水平分割线内容，设置额外css类名.

- strongStyle (dict; optional):
    针对文档中的加粗内容，设置额外css样式.

- strongClassName (string; optional):
    针对文档中的加粗内容，设置额外css类名.

- checkExternalLink (boolean; default False):
    是否针对文档内容中的外部链接进行安全检查，需配合有效的`safeRedirectUrlPrefix`  默认值：`False`.

- externalLinkPrefixWhiteList (list of strings; optional):
    当开启外部链接安全检查时，用于设置一系列白名单链接前缀，以这些白名单链接前缀开头的链接将忽略安全检查.

- safeRedirectUrlPrefix (string; optional):
    当开启外部链接安全检查时，用于定义链接点击跳转到的中转接口url前缀，譬如：
    针对外部链接`https://www.baidu.com/`，设置`safeRedirectUrlPrefix='/safe-redirect?target='`后，用户点击此外部链接，将跳转至
    `/safe-redirect?target=https://www.baidu.com/`.

- markdownBaseClassName (string; default 'markdown-body'):
    手动覆盖文档容器的css类名，通常在需要完全自定义文档样式时使用  默认值：`'markdown-body'`.

- titleAsId (boolean; default False):
    针对文档渲染结果中的各标题元素，是否将标题内容作为对应元素的id，以便于配合`AntdAnchor`等组件生成目录
    默认值：`False`.

- facAnchorLinkDict (boolean | number | string | dict | list; optional):
    监听基于文档标题内容自动推导计算出的目录结构，可直接配合`fac`组件库中的`AntdAnchor`组件使用.

- wrapLongLines (boolean; default False):
    针对超长行内容是否允许自动换行  默认值：`True`.

- codeFallBackLanguage (string; optional):
    当文档中存在源语言描述缺失的代码块时，设置缺省回滚的编程语言类型.

- searchKeyword (string; optional):
    搜索关键词.

- highlightStyle (dict; optional):
    `searchKeyword`对应搜索结果额外css样式.

- highlightClassName (string; optional):
    `searchKeyword`对应搜索结果额外css类名.

- mermaidOptions (dict; default False):
    针对代码块中的`mermaid`类型代码，配置图表渲染相关功能参数  默认值：`False`.

    `mermaidOptions` is a boolean | dict with keys:

    - theme (a value equal to: 'default', 'base', 'dark', 'forest', 'neutral', 'null'; optional):
        `mermaid`图表内置主题，可选项有`'default'`、`'base'`、`'dark'`、`'forest'`、`'neutral'`、`'None'`.

- mermaidContainerClassName (string; default '_mermaid-container'):
    当开启`mermaid`图表渲染功能时，为各图表所在容器设置统一的`css`类名
    默认值：`'_mermaid-container'`."""
    _children_props = ['placeholder']
    _base_nodes = ['placeholder', 'children']
    _namespace = 'feffery_markdown_components'
    _type = 'FefferyMarkdown'
    MermaidOptions = TypedDict(
        "MermaidOptions",
            {
            "theme": NotRequired[Literal["default", "base", "dark", "forest", "neutral", "null"]]
        }
    )


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        key: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        className: typing.Optional[str] = None,
        locale: typing.Optional[Literal["en-us", "zh-cn"]] = None,
        markdownStr: typing.Optional[str] = None,
        placeholder: typing.Optional[ComponentType] = None,
        codeTheme: typing.Optional[Literal["a11y-dark", "atom-dark", "coldark-cold", "coldark-dark", "coy", "coy-without-shadows", "darcula", "dracula", "nord", "okaidia", "prism", "solarizedlight", "twilight", "duotone-sea", "duotone-dark", "duotone-light", "duotone-space", "gh-colors", "gruvbox-dark", "material-dark", "night-owl", "one-light", "pojoaque", "solarized-dark-atom", "synthwave84", "z-touch"]] = None,
        renderHtml: typing.Optional[bool] = None,
        linkTarget: typing.Optional[str] = None,
        linkTransformFunc: typing.Optional[str] = None,
        codeBlockStyle: typing.Optional[dict] = None,
        codeStyle: typing.Optional[dict] = None,
        showLineNumbers: typing.Optional[bool] = None,
        showCopyButton: typing.Optional[bool] = None,
        imagePreview: typing.Optional[bool] = None,
        imageFallback: typing.Optional[str] = None,
        imageForceAlignCenter: typing.Optional[bool] = None,
        imageWidth: typing.Optional[typing.Union[str, NumberType]] = None,
        imageHeight: typing.Optional[typing.Union[str, NumberType]] = None,
        forceTableAlignCenter: typing.Optional[bool] = None,
        forceTableHeaderTextAlignCenter: typing.Optional[bool] = None,
        forceTableContentTextAlignCenter: typing.Optional[bool] = None,
        h1Style: typing.Optional[dict] = None,
        h1ClassName: typing.Optional[str] = None,
        h2Style: typing.Optional[dict] = None,
        h2ClassName: typing.Optional[str] = None,
        h3Style: typing.Optional[dict] = None,
        h3ClassName: typing.Optional[str] = None,
        h4Style: typing.Optional[dict] = None,
        h4ClassName: typing.Optional[str] = None,
        h5Style: typing.Optional[dict] = None,
        h5ClassName: typing.Optional[str] = None,
        h6Style: typing.Optional[dict] = None,
        h6ClassName: typing.Optional[str] = None,
        tableStyle: typing.Optional[dict] = None,
        tableClassName: typing.Optional[str] = None,
        theadStyle: typing.Optional[dict] = None,
        theadClassName: typing.Optional[str] = None,
        trStyle: typing.Optional[str] = None,
        trClassName: typing.Optional[str] = None,
        thStyle: typing.Optional[dict] = None,
        thClassName: typing.Optional[str] = None,
        tdStyle: typing.Optional[str] = None,
        tdClassName: typing.Optional[str] = None,
        aStyle: typing.Optional[dict] = None,
        aClassName: typing.Optional[str] = None,
        blockquoteStyle: typing.Optional[dict] = None,
        blockquoteClassName: typing.Optional[str] = None,
        inlineCodeStyle: typing.Optional[dict] = None,
        inlineCodeClassName: typing.Optional[str] = None,
        hrStyle: typing.Optional[dict] = None,
        hrClassName: typing.Optional[str] = None,
        strongStyle: typing.Optional[dict] = None,
        strongClassName: typing.Optional[str] = None,
        checkExternalLink: typing.Optional[bool] = None,
        externalLinkPrefixWhiteList: typing.Optional[typing.Sequence[str]] = None,
        safeRedirectUrlPrefix: typing.Optional[str] = None,
        markdownBaseClassName: typing.Optional[str] = None,
        titleAsId: typing.Optional[bool] = None,
        facAnchorLinkDict: typing.Optional[typing.Any] = None,
        wrapLongLines: typing.Optional[bool] = None,
        codeFallBackLanguage: typing.Optional[str] = None,
        searchKeyword: typing.Optional[str] = None,
        highlightStyle: typing.Optional[dict] = None,
        highlightClassName: typing.Optional[str] = None,
        mermaidOptions: typing.Optional[typing.Union[bool, "MermaidOptions"]] = None,
        mermaidContainerClassName: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'key', 'children', 'style', 'className', 'locale', 'markdownStr', 'placeholder', 'codeTheme', 'renderHtml', 'linkTarget', 'linkTransformFunc', 'codeBlockStyle', 'codeStyle', 'showLineNumbers', 'showCopyButton', 'imagePreview', 'imageFallback', 'imageForceAlignCenter', 'imageWidth', 'imageHeight', 'forceTableAlignCenter', 'forceTableHeaderTextAlignCenter', 'forceTableContentTextAlignCenter', 'h1Style', 'h1ClassName', 'h2Style', 'h2ClassName', 'h3Style', 'h3ClassName', 'h4Style', 'h4ClassName', 'h5Style', 'h5ClassName', 'h6Style', 'h6ClassName', 'tableStyle', 'tableClassName', 'theadStyle', 'theadClassName', 'trStyle', 'trClassName', 'thStyle', 'thClassName', 'tdStyle', 'tdClassName', 'aStyle', 'aClassName', 'blockquoteStyle', 'blockquoteClassName', 'inlineCodeStyle', 'inlineCodeClassName', 'hrStyle', 'hrClassName', 'strongStyle', 'strongClassName', 'checkExternalLink', 'externalLinkPrefixWhiteList', 'safeRedirectUrlPrefix', 'markdownBaseClassName', 'titleAsId', 'facAnchorLinkDict', 'wrapLongLines', 'codeFallBackLanguage', 'searchKeyword', 'highlightStyle', 'highlightClassName', 'mermaidOptions', 'mermaidContainerClassName']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'key', 'children', 'style', 'className', 'locale', 'markdownStr', 'placeholder', 'codeTheme', 'renderHtml', 'linkTarget', 'linkTransformFunc', 'codeBlockStyle', 'codeStyle', 'showLineNumbers', 'showCopyButton', 'imagePreview', 'imageFallback', 'imageForceAlignCenter', 'imageWidth', 'imageHeight', 'forceTableAlignCenter', 'forceTableHeaderTextAlignCenter', 'forceTableContentTextAlignCenter', 'h1Style', 'h1ClassName', 'h2Style', 'h2ClassName', 'h3Style', 'h3ClassName', 'h4Style', 'h4ClassName', 'h5Style', 'h5ClassName', 'h6Style', 'h6ClassName', 'tableStyle', 'tableClassName', 'theadStyle', 'theadClassName', 'trStyle', 'trClassName', 'thStyle', 'thClassName', 'tdStyle', 'tdClassName', 'aStyle', 'aClassName', 'blockquoteStyle', 'blockquoteClassName', 'inlineCodeStyle', 'inlineCodeClassName', 'hrStyle', 'hrClassName', 'strongStyle', 'strongClassName', 'checkExternalLink', 'externalLinkPrefixWhiteList', 'safeRedirectUrlPrefix', 'markdownBaseClassName', 'titleAsId', 'facAnchorLinkDict', 'wrapLongLines', 'codeFallBackLanguage', 'searchKeyword', 'highlightStyle', 'highlightClassName', 'mermaidOptions', 'mermaidContainerClassName']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(FefferyMarkdown, self).__init__(children=children, **args)

setattr(FefferyMarkdown, "__init__", _explicitize_args(FefferyMarkdown.__init__))
