# 攸然自得 · 时间线主题

以 DW Timeline Pro 为视觉参考的静态博客主题。文章源和主题分开维护。GitHub Actions 在每次推送 master 时，自动生成文章、时间线、年份筛选、归档、分类和标签，然后发布 GitHub Pages。

## 增删文章

每篇文章是 `posts/` 中的一个 JSON 文件。复制任意一篇，修改 title、date、path、body。body 为 HTML，可写段落、图片和视频。path 为唯一的文章地址，例如 `2026/09/30/hello/`。categories、tags 是含 name 属性的对象数组，也可留空。

```json
{
  "title": "今天的记录",
  "date": "2026-09-30",
  "path": "2026/09/30/hello/",
  "categories": [{"name": "日记"}],
  "tags": [],
  "body": "<p>今天的故事。</p><img src=\"/assets/photos/example.jpg\" alt=\"照片\">"
}
```

新增文件就是新增文章，删除对应源文件就是删除文章，修改文件就是编辑文章。提交到 master 后自动发布，无需手动修改首页。删除的文章页面也会在构建时移除。图片放在 `assets/photos/` 中。

本地预览：`python3 scripts/build-timeline.py`，再运行 `python3 -m http.server 8765`。

`timeline-posts.json` 是自动生成的数据，不要在这里编辑文章。主题模板为 `scripts/build-timeline.py`，样式和交互为 `assets/timeline/`。此仓库原本只有 Hexo 发布产物，因此目前采用独立静态主题生成器，不是可安装到另一个 Hexo 源项目的主题包。
