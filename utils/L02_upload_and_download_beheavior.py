# 上传行为模式
upload_patterns = [
    # GitHub Actions 上传相关
    r'actions/upload-artifact',
    r'actions/upload-pages-artifact',
    r'actions/deploy-pages',  # 部署通常是上传行为

    # 云服务上传
    r'aws-actions/.*s3.*upload',
    r'azure/.*upload',
    r'google-github-actions/.*upload',

    # 通用上传命令
    r'\bupload\b',
    r'\bscp\b',  # 通常用于上传文件到远程服务器
    r'\bsftp\b',  # 安全文件传输，可上传可下载，但更多用于上传
    r'\bftp\b',   # 文件传输协议，可上传可下载
    r'\brsync\b', # 文件同步，可上传可下载
    r'\bcurl.*--upload-file\b',

    # 包管理器发布（上传）
    r'\bnpm publish\b',
    r'\byarn publish\b',
    r'\bpip upload\b',
    r'\btwine upload\b',
    r'\bmaven deploy\b',
    r'\bgradle publish\b',
    r'\bdocker push\b',

    # 文件传输相关（上传）
    r'\bput\s+\w+',
    r'\bsend\s+\w+',
    r'\btransfer\s+\w+',  # 可上传可下载，但常用于上传

    # API 调用相关（上传）
    r'POST.*upload',
    r'PUT.*upload',

    # 存储服务上传
    r's3.*cp',     # 可上传可下载，但常用于上传
    r's3.*sync',   # 同步操作，可上传可下载
    r'gsutil.*cp', # 可上传可下载
    r'gsutil.*rsync',
    r'az.*upload',

    # 版本控制相关（上传）
    r'git push',

    # 备份/恢复（上传）
    r'\bbackup\b',
    r'\barchive\b',
]

# 下载行为模式
download_patterns = [
    # GitHub Actions 下载相关
    r'actions/download-artifact',

    # 云服务下载
    r'aws-actions/.*s3.*download',
    r'azure/.*download',
    r'google-github-actions/.*download',

    # 通用下载命令
    r'\bdownload\b',
    r'\bwget\b',
    r'\bcurl.*-o\b',
    r'\bcurl.*--output\b',

    # 包管理器安装（下载）
    r'\bnpm install\b',
    r'\bpip install\b',
    r'\bdocker pull\b',

    # 文件传输相关（下载）
    r'\bget\s+\w+',
    r'\breceive\s+\w+',

    # API 调用相关（下载）
    r'GET.*download',

    # 存储服务下载
    r'az.*download',

    # 版本控制相关（下载）
    r'git pull',
    r'git fetch',
    r'git clone',

    # 备份/恢复（下载）
    r'\brestore\b',
    r'\bunzip\b',
    r'\buntar\b',
    r'\bextract\b',
]

# 双向操作模式（既可上传也可下载，需要根据上下文判断）
bidirectional_patterns = [
    # 这些模式需要结合具体的命令参数或上下文来判断方向
    r'\bscp\b',      # 根据源和目标路径判断
    r'\bsftp\b',     # 需要看具体命令
    r'\bftp\b',      # 需要看具体命令
    r'\brsync\b',    # 需要看源和目标路径
    r's3.*cp',       # 需要看源和目标路径
    r's3.*sync',     # 需要看源和目标路径
    r'gsutil.*cp',   # 需要看源和目标路径
    r'gsutil.*rsync',
    r'\btransfer\s+\w+',  # 需要看上下文
]

# YAML 模式分类
yaml_upload_patterns = [
    r'uses:.*upload',
    r'with:.*path:.*upload',
    r'run:.*upload',
]

yaml_download_patterns = [
    r'uses:.*download',
    r'with:.*path:.*download',
    r'run:.*download',
]