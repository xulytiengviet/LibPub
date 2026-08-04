(() => {
  "use strict";

  const messages = {
    vi: {
      "page.title": "LibPub · Xuất bản preprint trên GitHub", "page.skip": "Đi đến nội dung", "footer.source": "Mã nguồn",
      "nav.catalog": "Kho preprint", "nav.workflow": "Quy trình", "nav.submit": "Gửi bản thảo", "nav.github": "GitHub ↗",
      "hero.eyebrow": "GitHub-native preprint publishing", "hero.title": "Biến một repository thành <em>máy chủ xuất bản</em> khoa học.",
      "hero.description": "Nhận DOCX hoặc JATS XML, kiểm tra metadata, sinh HTML/PDF, tạo GitHub Release và đồng bộ DOI Zenodo—không cần máy chủ động.",
      "hero.submit": "Gửi bản thảo ngay", "hero.guide": "Xem hướng dẫn", "hero.trust1": "✓ Lịch sử phiên bản Git", "hero.trust2": "✓ HTML + PDF + XML", "hero.trust3": "✓ DOI Zenodo",
      "console.input": "Đầu vào", "console.preprints": "Preprint", "console.authors": "Tác giả", "console.formats": "Định dạng",
      "workflow.kicker": "TỰ ĐỘNG HÓA TOÀN TRÌNH", "workflow.title": "Một lần gửi, ba định dạng và một DOI", "workflow.description": "Pipeline có thể tái lập, kiểm tra được và lưu toàn bộ thay đổi trong lịch sử Git.",
      "workflow.s1.title": "Nhận bản thảo", "workflow.s1.text": "DOCX hoặc JATS XML kèm metadata JSON.",
      "workflow.s2.title": "Chuẩn hóa", "workflow.s2.text": "XSweet làm sạch DOCX; Pandoc tạo JATS.",
      "workflow.s3.title": "Kiểm tra", "workflow.s3.text": "DOI, ORCID, metadata và XML được xác thực.",
      "workflow.s4.title": "Dàn trang", "workflow.s4.text": "Sinh HTML học thuật, PDF và release assets.",
      "workflow.s5.title": "DOI & công bố", "workflow.s5.text": "Release kích hoạt Zenodo, DOI được ghi lại vào trang.",
      "catalog.kicker": "KHO CÔNG BỐ", "catalog.title": "Preprint mới nhất", "catalog.search": "Tìm tiêu đề, tác giả, từ khóa…", "catalog.all": "Mọi ngôn ngữ",
      "submit.kicker": "BẢNG ĐIỀU KHIỂN TÁC GIẢ", "submit.title": "Gửi và công bố bản thảo", "submit.description": "Điền metadata, chọn DOCX hoặc XML và gửi một commit nguyên tử. GitHub Actions sẽ xử lý từ bản thảo đến DOI.",
      "submit.c1": "Khai báo", "submit.c1s": "Thông tin bài báo và tác giả", "submit.c2": "Đính kèm", "submit.c2s": "manuscript.docx hoặc article.xml", "submit.c3": "Xác thực", "submit.c3s": "Token chỉ giữ trong bộ nhớ phiên", "submit.c4": "Submit", "submit.c4s": "Commit kích hoạt build, release và DOI",
      "submit.doi.title": "Nguyên tắc DOI", "submit.doi.text": "DOI nhập tay phải được cấp hợp lệ. Nếu để trống, LibPub có thể tạo DOI Zenodo sau khi merge và release.",
      "submit.zenodo.title": "Thiết lập Zenodo một lần", "submit.zenodo.text": "Chủ repository cần kết nối GitHub, bấm Sync now và bật công tắc LibPub.", "submit.zenodo.link": "Mở Zenodo GitHub Settings ↗",
      "form.progress.meta": "01 Metadata", "form.progress.file": "02 Tệp", "form.progress.github": "03 GitHub", "form.article": "Thông tin bài báo", "form.authors": "Tác giả", "form.source": "Bản thảo và GitHub",
      "form.title": "Tiêu đề", "form.slug": "Định danh đường dẫn", "form.doi": "DOI đã được cấp", "form.abstract": "Tóm tắt", "form.keywords": "Từ khóa", "form.language": "Ngôn ngữ", "form.type": "Loại bài", "form.date": "Ngày công bố", "form.license": "Giấy phép", "form.version": "Phiên bản", "form.status": "Trạng thái",
      "form.given": "Tên", "form.family": "Họ", "form.orcid": "ORCID", "form.email": "Email liên hệ", "form.affiliation": "Cơ quan công tác", "form.addAuthor": "＋ Thêm đồng tác giả",
      "form.titlePlaceholder": "Nhập tiêu đề đầy đủ của bản thảo", "form.slugPlaceholder": "ten-bai-bao", "form.abstractPlaceholder": "Mục tiêu, phương pháp, kết quả chính và đóng góp…", "form.charCount": "/10.000 ký tự", "form.keywordsHint": "Phân tách bằng dấu chấm phẩy.", "form.affiliationPlaceholder": "Tên trường, viện hoặc tổ chức",
      "form.file": "Chọn manuscript.docx hoặc article.xml", "form.fileHint": "Tối đa 25 MB · tệp chỉ được gửi khi bấm Submit", "form.branch": "Nhánh công bố", "form.token": "Fine-grained token", "form.tokenHint": "Resource owner: xulytiengviet · Only select repositories: LibPub · Contents: Read and write.", "form.createToken": "Tạo token đúng quyền ↗", "form.checkToken": "Kiểm tra token",
      "form.confirm": "Tôi xác nhận DOI nhập tay (nếu có) hợp lệ và tôi có quyền công bố bản thảo này.", "form.download": "Tải metadata.json", "form.publish": "Submit & Publish", "form.tokenPolicy": "Token không được ghi vào storage, URL, log hay tệp tải xuống. Hãy thu hồi token sau khi không còn sử dụng.",
      "catalog.read": "Đọc toàn văn →", "catalog.noDoi": "Đang chờ DOI", "catalog.empty": "Kho preprint sẽ xuất hiện sau lần build đầu tiên.", "catalog.noMatch": "Chưa tìm thấy bài báo phù hợp.",
      "type.research": "Bài nghiên cứu", "type.review": "Bài tổng quan", "type.methods": "Bài phương pháp", "type.data": "Bài dữ liệu", "type.policy": "Bài chính sách", "type.case": "Báo cáo trường hợp", "type.other": "Khác", "license.arr": "Bảo lưu mọi quyền",
      "status.preprint": "Preprint", "status.revised": "Đã sửa", "status.published": "Đã xuất bản", "status.withdrawn": "Đã rút",
      "coauthor.title": "Đồng tác giả", "coauthor.remove": "Xóa",
      "error.slug": "Định danh đường dẫn không hợp lệ.", "error.title": "Tiêu đề phải có ít nhất 10 ký tự.", "error.abstract": "Tóm tắt phải có ít nhất 20 ký tự.", "error.keywords": "Cần ít nhất một từ khóa.", "error.doi": "DOI không đúng cú pháp.", "error.version": "Phiên bản phải là số nguyên từ 1.", "error.author": "Tác giả {n} thiếu họ hoặc tên.", "error.orcid": "ORCID của tác giả {n} không hợp lệ hoặc sai checksum.", "error.noFile": "Chưa chọn bản thảo DOCX hoặc XML.", "error.fileType": "LibPub chỉ nhận tệp .docx hoặc .xml.", "error.fileSize": "Tệp vượt quá giới hạn 25 MB của dashboard.", "error.formMeta": "Hãy nhập tiêu đề và định danh trước khi tải metadata.", "error.disabled": "Chức năng công bố trực tiếp đã bị tắt trong publication.config.json.", "error.token": "Cần fine-grained token để ghi commit vào GitHub.", "error.githubNetwork": "Không kết nối được GitHub API. Hãy kiểm tra Internet, VPN hoặc tiện ích chặn request.", "error.github401": "Token không hợp lệ, đã hết hạn hoặc bị thu hồi. Hãy tạo token mới; LibPub đã tự loại bỏ tiền tố Bearer/token, dấu nháy và khoảng trắng khi dán.", "error.github403": "Token hợp lệ nhưng không có quyền push. Chọn Resource owner xulytiengviet, repository LibPub và Contents: Read and write; đồng thời kiểm tra token có đang chờ phê duyệt hay không.", "error.github404": "Token không truy cập được {repository} hoặc nhánh đã nhập. Kiểm tra Resource owner và Selected repositories.", "error.github409": "Nhánh vừa thay đổi trong lúc gửi. Hãy tải lại trang và thử lại để tránh ghi đè commit mới.", "error.github410": "Phiên bản GitHub API không còn được hỗ trợ. Hãy cập nhật LibPub.", "error.github422": "GitHub từ chối cập nhật ref. Nhánh có thể được bảo vệ hoặc commit không còn là fast-forward; hãy gửi bằng pull request.", "error.githubGeneric": "GitHub API lỗi {status}: {detail}", "error.githubPermissions": "Quyền endpoint yêu cầu: {permissions}.",
      "status.metadata": "Đã tạo metadata.json. Đặt tệp này cùng article.xml hoặc manuscript.docx trong articles/<slug>/.", "status.verifyingToken": "Đang xác thực token, repository và nhánh trên GitHub…", "status.tokenValid": "Token hợp lệ: @{login} có thể truy cập {repository}, nhánh {branch}.", "status.preparing": "Đang xác thực repository và chuẩn bị commit nguyên tử…", "status.uploading": "Đang tải metadata và bản thảo lên GitHub…", "status.cancelled": "Đã hủy thao tác; repository chưa thay đổi.", "status.noToken": "Không token nào được lưu lại.", "confirm.exists": "Bài '{slug}' đã tồn tại. Tiếp tục sẽ tạo phiên bản mới và thay tệp trùng tên. Tiếp tục?", "publish.success": "Đã tạo commit {commit}. Theo dõi {actions}; trang bài báo sẽ xuất hiện sau khi pipeline hoàn tất.",
      "lang.label": "Ngôn ngữ giao diện"
    },
    en: {
      "page.title": "LibPub · Publish preprints on GitHub", "page.skip": "Skip to content", "footer.source": "Source code",
      "nav.catalog": "Preprint archive", "nav.workflow": "Workflow", "nav.submit": "Submit", "nav.github": "GitHub ↗",
      "hero.eyebrow": "GitHub-native preprint publishing", "hero.title": "Turn a repository into a scholarly <em>publishing server</em>.",
      "hero.description": "Accept DOCX or JATS XML, validate metadata, generate HTML/PDF, create GitHub Releases and synchronize Zenodo DOIs—without a dynamic server.",
      "hero.submit": "Submit a manuscript", "hero.guide": "Read the guide", "hero.trust1": "✓ Git version history", "hero.trust2": "✓ HTML + PDF + XML", "hero.trust3": "✓ Zenodo DOI",
      "console.input": "Input", "console.preprints": "Preprints", "console.authors": "Authors", "console.formats": "Formats",
      "workflow.kicker": "END-TO-END AUTOMATION", "workflow.title": "One submission, three formats and one DOI", "workflow.description": "A reproducible, auditable pipeline with every change preserved in Git history.",
      "workflow.s1.title": "Receive", "workflow.s1.text": "DOCX or JATS XML with JSON metadata.", "workflow.s2.title": "Normalize", "workflow.s2.text": "XSweet cleans DOCX; Pandoc generates JATS.", "workflow.s3.title": "Validate", "workflow.s3.text": "DOI, ORCID, metadata and XML are checked.", "workflow.s4.title": "Typeset", "workflow.s4.text": "Generate scholarly HTML, PDF and release assets.", "workflow.s5.title": "DOI & publish", "workflow.s5.text": "A Release triggers Zenodo; the DOI is written back to the site.",
      "catalog.kicker": "PUBLICATION ARCHIVE", "catalog.title": "Latest preprints", "catalog.search": "Search title, author or keyword…", "catalog.all": "All languages",
      "submit.kicker": "AUTHOR CONSOLE", "submit.title": "Submit and publish a manuscript", "submit.description": "Enter metadata, select DOCX or XML and create one atomic commit. GitHub Actions handles the path from manuscript to DOI.",
      "submit.c1": "Describe", "submit.c1s": "Article and author metadata", "submit.c2": "Attach", "submit.c2s": "manuscript.docx or article.xml", "submit.c3": "Authorize", "submit.c3s": "Token remains in session memory", "submit.c4": "Submit", "submit.c4s": "Commit triggers build, release and DOI",
      "submit.doi.title": "DOI policy", "submit.doi.text": "A manually entered DOI must already be valid. Leave it blank to let LibPub mint a Zenodo DOI after merge and release.",
      "submit.zenodo.title": "One-time Zenodo setup", "submit.zenodo.text": "The repository owner must connect GitHub, click Sync now and enable the LibPub toggle.", "submit.zenodo.link": "Open Zenodo GitHub Settings ↗",
      "form.progress.meta": "01 Metadata", "form.progress.file": "02 File", "form.progress.github": "03 GitHub", "form.article": "Article information", "form.authors": "Authors", "form.source": "Manuscript and GitHub",
      "form.title": "Title", "form.slug": "URL identifier", "form.doi": "Existing DOI", "form.abstract": "Abstract", "form.keywords": "Keywords", "form.language": "Language", "form.type": "Article type", "form.date": "Publication date", "form.license": "License", "form.version": "Version", "form.status": "Status",
      "form.given": "Given name", "form.family": "Family name", "form.orcid": "ORCID", "form.email": "Contact email", "form.affiliation": "Affiliation", "form.addAuthor": "＋ Add co-author",
      "form.titlePlaceholder": "Enter the full manuscript title", "form.slugPlaceholder": "article-slug", "form.abstractPlaceholder": "Objective, methods, main results and contribution…", "form.charCount": "/10,000 characters", "form.keywordsHint": "Separate terms with semicolons.", "form.affiliationPlaceholder": "University, institute or organization",
      "form.file": "Choose manuscript.docx or article.xml", "form.fileHint": "Maximum 25 MB · uploaded only after Submit", "form.branch": "Publication branch", "form.token": "Fine-grained token", "form.tokenHint": "Resource owner: xulytiengviet · Only select repositories: LibPub · Contents: Read and write.", "form.createToken": "Create the correct token ↗", "form.checkToken": "Check token",
      "form.confirm": "I confirm that any manually entered DOI is valid and that I have the right to publish this manuscript.", "form.download": "Download metadata.json", "form.publish": "Submit & Publish", "form.tokenPolicy": "The token is never written to storage, URLs, logs or downloads. Revoke it when no longer needed.",
      "catalog.read": "Read full text →", "catalog.noDoi": "DOI pending", "catalog.empty": "Preprints will appear after the first build.", "catalog.noMatch": "No matching article found.",
      "type.research": "Research article", "type.review": "Review article", "type.methods": "Methods article", "type.data": "Data paper", "type.policy": "Policy paper", "type.case": "Case report", "type.other": "Other", "license.arr": "All rights reserved",
      "status.preprint": "Preprint", "status.revised": "Revised", "status.published": "Published", "status.withdrawn": "Withdrawn",
      "coauthor.title": "Co-author", "coauthor.remove": "Remove",
      "error.slug": "The URL identifier is invalid.", "error.title": "The title must contain at least 10 characters.", "error.abstract": "The abstract must contain at least 20 characters.", "error.keywords": "At least one keyword is required.", "error.doi": "The DOI syntax is invalid.", "error.version": "The version must be an integer of 1 or greater.", "error.author": "Author {n} is missing a given or family name.", "error.orcid": "Author {n} has an invalid ORCID or checksum.", "error.noFile": "Select a DOCX or XML manuscript.", "error.fileType": "LibPub accepts only .docx or .xml files.", "error.fileSize": "The file exceeds the dashboard's 25 MB limit.", "error.formMeta": "Enter a title and URL identifier before downloading metadata.", "error.disabled": "Direct publishing is disabled in publication.config.json.", "error.token": "A fine-grained token is required to commit to GitHub.", "error.githubNetwork": "GitHub API could not be reached. Check your Internet connection, VPN or request-blocking extension.", "error.github401": "The token is invalid, expired or revoked. Create a new token; LibPub now removes pasted Bearer/token prefixes, quotes and whitespace automatically.", "error.github403": "The token is valid but cannot push. Select resource owner xulytiengviet, repository LibPub and Contents: Read and write; also check whether approval is pending.", "error.github404": "The token cannot access {repository} or the selected branch. Check the resource owner and selected repositories.", "error.github409": "The branch changed during submission. Reload and retry to avoid overwriting a newer commit.", "error.github410": "This GitHub API version is no longer supported. Update LibPub.", "error.github422": "GitHub rejected the ref update. The branch may be protected or the commit is no longer a fast-forward; submit through a pull request.", "error.githubGeneric": "GitHub API error {status}: {detail}", "error.githubPermissions": "Endpoint permissions: {permissions}.",
      "status.metadata": "metadata.json is ready. Place it beside article.xml or manuscript.docx in articles/<slug>/.", "status.verifyingToken": "Verifying the token, repository and branch on GitHub…", "status.tokenValid": "Valid token: @{login} can access {repository}, branch {branch}.", "status.preparing": "Checking the repository and preparing an atomic commit…", "status.uploading": "Uploading metadata and the manuscript to GitHub…", "status.cancelled": "Operation cancelled; the repository was not changed.", "status.noToken": "No token was stored.", "confirm.exists": "Article '{slug}' already exists. Continuing creates a new version and replaces files with the same name. Continue?", "publish.success": "Created commit {commit}. Follow {actions}; the article page will appear when the pipeline completes.",
      "lang.label": "Interface language"
    },
    zh: {
      "page.title": "LibPub · 在 GitHub 上发布预印本", "page.skip": "跳至正文", "footer.source": "源代码",
      "nav.catalog": "预印本库", "nav.workflow": "出版流程", "nav.submit": "提交稿件", "nav.github": "GitHub ↗",
      "hero.eyebrow": "GitHub 原生预印本出版", "hero.title": "将代码仓库变成学术<em>出版服务器</em>。", "hero.description": "接收 DOCX 或 JATS XML，校验元数据，生成 HTML/PDF，创建 GitHub Release 并同步 Zenodo DOI，无需动态服务器。",
      "hero.submit": "立即投稿", "hero.guide": "查看指南", "hero.trust1": "✓ Git 版本历史", "hero.trust2": "✓ HTML + PDF + XML", "hero.trust3": "✓ Zenodo DOI",
      "console.input": "输入", "console.preprints": "预印本", "console.authors": "作者", "console.formats": "格式",
      "workflow.kicker": "端到端自动化", "workflow.title": "一次提交，三种格式，一个 DOI", "workflow.description": "可复现、可审计的流水线，所有变更均保存在 Git 历史中。",
      "workflow.s1.title": "接收稿件", "workflow.s1.text": "DOCX 或 JATS XML 及 JSON 元数据。", "workflow.s2.title": "规范化", "workflow.s2.text": "XSweet 清理 DOCX，Pandoc 生成 JATS。", "workflow.s3.title": "校验", "workflow.s3.text": "检查 DOI、ORCID、元数据和 XML。", "workflow.s4.title": "排版", "workflow.s4.text": "生成学术 HTML、PDF 和 Release 附件。", "workflow.s5.title": "DOI 与发布", "workflow.s5.text": "Release 触发 Zenodo，DOI 自动回写网站。",
      "catalog.kicker": "出版档案", "catalog.title": "最新预印本", "catalog.search": "搜索标题、作者或关键词…", "catalog.all": "全部语言",
      "submit.kicker": "作者控制台", "submit.title": "提交并发布稿件", "submit.description": "填写元数据，选择 DOCX 或 XML，并创建一个原子提交。GitHub Actions 自动完成从稿件到 DOI 的流程。",
      "submit.c1": "填写信息", "submit.c1s": "论文与作者元数据", "submit.c2": "上传文件", "submit.c2s": "manuscript.docx 或 article.xml", "submit.c3": "授权", "submit.c3s": "令牌仅保存在会话内存", "submit.c4": "提交", "submit.c4s": "提交触发构建、Release 与 DOI",
      "submit.doi.title": "DOI 原则", "submit.doi.text": "手动填写的 DOI 必须已合法注册。留空则可在合并和发布后由 LibPub 创建 Zenodo DOI。",
      "submit.zenodo.title": "一次性设置 Zenodo", "submit.zenodo.text": "仓库所有者需要连接 GitHub，点击 Sync now，并启用 LibPub 开关。", "submit.zenodo.link": "打开 Zenodo GitHub 设置 ↗",
      "form.progress.meta": "01 元数据", "form.progress.file": "02 文件", "form.progress.github": "03 GitHub", "form.article": "论文信息", "form.authors": "作者", "form.source": "稿件与 GitHub",
      "form.title": "标题", "form.slug": "网址标识", "form.doi": "已有 DOI", "form.abstract": "摘要", "form.keywords": "关键词", "form.language": "语言", "form.type": "论文类型", "form.date": "发布日期", "form.license": "许可证", "form.version": "版本", "form.status": "状态",
      "form.given": "名", "form.family": "姓", "form.orcid": "ORCID", "form.email": "联系邮箱", "form.affiliation": "所属机构", "form.addAuthor": "＋ 添加共同作者",
      "form.titlePlaceholder": "请输入稿件完整标题", "form.slugPlaceholder": "article-slug", "form.abstractPlaceholder": "研究目标、方法、主要结果与贡献…", "form.charCount": "/10,000 字符", "form.keywordsHint": "请使用分号分隔关键词。", "form.affiliationPlaceholder": "大学、研究机构或组织名称",
      "form.file": "选择 manuscript.docx 或 article.xml", "form.fileHint": "最大 25 MB · 点击提交后才会上传", "form.branch": "发布分支", "form.token": "细粒度令牌", "form.tokenHint": "资源所有者：xulytiengviet · 仅选择仓库：LibPub · Contents：读写。", "form.createToken": "创建正确权限的令牌 ↗", "form.checkToken": "检查令牌",
      "form.confirm": "我确认手动填写的 DOI（如有）有效，并拥有发布该稿件的权利。", "form.download": "下载 metadata.json", "form.publish": "提交并发布", "form.tokenPolicy": "令牌不会写入存储、网址、日志或下载文件。不再使用时请撤销令牌。",
      "catalog.read": "阅读全文 →", "catalog.noDoi": "DOI 生成中", "catalog.empty": "首次构建后，预印本将在此显示。", "catalog.noMatch": "未找到匹配的论文。",
      "type.research": "研究论文", "type.review": "综述论文", "type.methods": "方法论文", "type.data": "数据论文", "type.policy": "政策论文", "type.case": "病例报告", "type.other": "其他", "license.arr": "保留所有权利",
      "status.preprint": "预印本", "status.revised": "修订版", "status.published": "已出版", "status.withdrawn": "已撤稿",
      "coauthor.title": "共同作者", "coauthor.remove": "删除",
      "error.slug": "网址标识格式无效。", "error.title": "标题不得少于 10 个字符。", "error.abstract": "摘要不得少于 20 个字符。", "error.keywords": "至少需要一个关键词。", "error.doi": "DOI 格式无效。", "error.version": "版本必须是大于或等于 1 的整数。", "error.author": "作者 {n} 缺少姓或名。", "error.orcid": "作者 {n} 的 ORCID 或校验位无效。", "error.noFile": "请选择 DOCX 或 XML 稿件。", "error.fileType": "LibPub 仅接受 .docx 或 .xml 文件。", "error.fileSize": "文件超过控制台 25 MB 限制。", "error.formMeta": "下载元数据前，请先填写标题和网址标识。", "error.disabled": "publication.config.json 已禁用直接发布。", "error.token": "提交至 GitHub 需要细粒度令牌。", "error.githubNetwork": "无法连接 GitHub API。请检查网络、VPN 或拦截请求的浏览器扩展。", "error.github401": "令牌无效、已过期或已撤销。请创建新令牌；LibPub 会自动清除粘贴内容中的 Bearer/token 前缀、引号和空格。", "error.github403": "令牌有效但没有推送权限。请选择资源所有者 xulytiengviet、仓库 LibPub，并授予 Contents 读写权限；同时检查是否仍在等待审批。", "error.github404": "令牌无法访问 {repository} 或所选分支。请检查资源所有者和已选择的仓库。", "error.github409": "提交期间分支已发生变化。请刷新页面后重试，以免覆盖较新的提交。", "error.github410": "当前 GitHub API 版本已不受支持。请更新 LibPub。", "error.github422": "GitHub 拒绝更新引用。分支可能受保护，或提交已不是快进更新；请改用 pull request。", "error.githubGeneric": "GitHub API 错误 {status}：{detail}", "error.githubPermissions": "接口所需权限：{permissions}。",
      "status.metadata": "metadata.json 已生成。请将其与 article.xml 或 manuscript.docx 一同放入 articles/<slug>/。", "status.verifyingToken": "正在 GitHub 上验证令牌、仓库和分支…", "status.tokenValid": "令牌有效：@{login} 可访问 {repository} 的 {branch} 分支。", "status.preparing": "正在检查代码仓库并准备原子提交…", "status.uploading": "正在将元数据和稿件上传至 GitHub…", "status.cancelled": "操作已取消，代码仓库未发生更改。", "status.noToken": "未保存任何令牌。", "confirm.exists": "论文“{slug}”已存在。继续操作将创建新版本并替换同名文件。是否继续？", "publish.success": "已创建提交 {commit}。请查看 {actions}；流水线完成后论文页面将自动上线。",
      "lang.label": "界面语言"
    }
  };

  function translate(key, fallback = "") {
    const lang = document.documentElement.dataset.uiLanguage || "vi";
    return messages[lang]?.[key] ?? messages.vi[key] ?? fallback;
  }

  function apply(lang) {
    const selected = messages[lang] ? lang : "vi";
    document.documentElement.dataset.uiLanguage = selected;
    document.documentElement.lang = selected === "zh" ? "zh-CN" : selected;
    document.title = translate("page.title", document.title);
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      node.textContent = translate(node.dataset.i18n, node.textContent);
    });
    document.querySelectorAll("[data-i18n-html]").forEach((node) => {
      node.innerHTML = translate(node.dataset.i18nHtml, node.innerHTML);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
      node.placeholder = translate(node.dataset.i18nPlaceholder, node.placeholder);
    });
    const select = document.querySelector("#ui-language");
    if (select) select.value = selected;
    localStorage.setItem("libpub-language", selected);
    document.dispatchEvent(new CustomEvent("libpub:language", { detail: { language: selected } }));
  }

  window.LibPubI18n = { messages, translate, apply };
})();
