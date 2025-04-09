# 橙子就业分析平台

橙子就业是一个针对学校就业网招聘信息的数据分析平台，提供行业分布、薪资范围、地区分布等可视化分析，帮助学生了解就业市场动态，为职业规划提供参考。

## 项目结构

- `frontend/` - 前端Vue.js项目
- `job_analysis/` - Django应用，包含职位数据模型和API
- `orange_job/` - Django项目配置

## 技术栈

### 后端
- Python 3.11
- Django 5.0.2
- Django REST Framework
- MySQL

### 前端
- Vue.js 2.x
- Element UI
- ECharts

## 功能特点

- 从成都大学就业网自动获取最新招聘信息
- 查看职位列表，支持多条件筛选
- 职位详情展示
- 招聘数据分析，包括：
  - 行业分布分析
  - 薪资分布分析
  - 地区分布分析
  - 岗位类型分析
- 可视化图表展示分析结果

## 安装与运行

### 后端

1. 克隆项目
```
git clone <repository-url>
cd OrangeManage
```

2. 安装Python依赖
```
pip install -r requirements.txt
```

3. 配置数据库
在 `orange_job/settings.py` 中配置数据库连接

4. 运行数据库迁移
```
python manage.py migrate
```

5. 获取招聘数据
```
python manage.py fetch_cdu_jobs
```

6. 生成分析数据
```
python manage.py generate_analysis
```

7. 启动开发服务器
```
python manage.py runserver
```

### 前端

1. 进入前端目录
```
cd frontend
```

2. 安装依赖
```
npm install
```

3. 启动开发服务器
```
npm run serve
```

4. 构建生产版本
```
npm run build
```

## API文档

### 职位API
- `GET /api/jobs/` - 获取职位列表，支持分页和筛选
- `GET /api/jobs/:id/` - 获取职位详情

### 分析API
- `GET /api/analysis/all/` - 获取所有分析数据
- `GET /api/analysis/industry/` - 获取行业分布分析
- `GET /api/analysis/salary/` - 获取薪资分布分析
- `GET /api/analysis/location/` - 获取地区分布分析
- `GET /api/analysis/job_type/` - 获取岗位类型分析

## 项目结构

```
.
├── backend/                  # 后端Django项目
│   ├── job_analysis/        # 主应用
│   │   ├── api/             # API接口
│   │   ├── crawler/         # 爬虫模块
│   │   ├── models/          # 数据模型
│   │   └── utils/           # 工具类
│   └── orange_job/          # Django项目设置
├── frontend/                 # 前端Vue项目
│   ├── public/              # 静态资源
│   └── src/                 # 源代码
│       ├── api/             # API请求
│       ├── assets/          # 资源文件
│       ├── components/      # 组件
│       ├── router/          # 路由
│       ├── store/           # 状态管理
│       └── views/           # 视图
└── README.md                # 项目说明
```

## 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request 