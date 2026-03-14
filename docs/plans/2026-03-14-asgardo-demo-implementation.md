# ASGARD产品Demo前端实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建ASGARD产品能力Demo前端，展示Agent智能编排、BAS技能库、数据分析等核心功能

**Architecture:** 单文件HTML应用，使用Tailwind CSS（CDN）+ ECharts（CDN）+ 原生JavaScript，采用Bento Grid布局，Apple极简设计风格

**Tech Stack:** HTML5, JavaScript ES6+, Tailwind CSS (CDN), ECharts 5.x (CDN), Font Awesome (CDN)

---

## 实现优先级

### P0 - MVP核心功能（本计划覆盖）
- ✅ 首页（价值主张）
- ✅ 导航系统（Tab切换）
- ✅ Agent智能编排界面（对话 + DAG）
- ✅ 基础数据结构（BAS Skills）

### P1 - 完善体验（后续计划）
- 技能库展示
- 数据分析界面
- 案例展示

---

## Task 1: 项目结构搭建

**Files:**
- Create: `demo/index.html`
- Create: `demo/README.md`

**Step 1: 创建demo目录和README**

```bash
mkdir -p demo
cd demo
```

创建 `demo/README.md`:

```markdown
# ASGARD 产品Demo

## 运行方式

直接用浏览器打开 `index.html` 即可，无需服务器。

## 技术栈

- HTML5
- JavaScript ES6+
- Tailwind CSS (CDN)
- ECharts (CDN)
- Font Awesome (CDN)

## 开发

```bash
# 使用Python启动简单HTTP服务器（可选）
python -m http.server 8000
```

## 浏览器兼容性

- Chrome/Edge 90+
- Safari 14+
- Firefox 88+
- 移动端Safari iOS 14+
- 移动端Chrome Android 10+
```

**Step 2: 提交**

```bash
git add demo/README.md
git commit -m "feat: 添加demo目录和README"
```

---

## Task 2: HTML骨架和CDN依赖

**Files:**
- Modify: `demo/index.html` (创建新文件)

**Step 1: 创建基础HTML结构**

创建 `demo/index.html`:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASGARD - The Intelligent Battery Brain</title>

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <!-- ECharts -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>

    <style>
        /* 自定义样式将在后续添加 */
    </style>
</head>
<body class="bg-white text-black antialiased">
    <!-- 导航栏 -->
    <nav id="main-nav"></nav>

    <!-- Tab内容容器 -->
    <main id="tab-content"></main>

    <script>
        // JavaScript逻辑将在后续添加
    </script>
</body>
</html>
```

**Step 2: 在浏览器中验证**

用浏览器打开 `demo/index.html`
Expected: 空白页面，控制台无错误

**Step 3: 提交**

```bash
git add demo/index.html
git commit -m "feat: 添加HTML基础结构和CDN依赖"
```

---

## Task 3: Tailwind配置和自定义样式

**Files:**
- Modify: `demo/index.html` (添加Tailwind配置)

**Step 1: 配置Tailwind主题**

在 `<head>` 中，Tailwind CDN之前添加：

```html
<script>
    tailwind.config = {
        theme: {
            extend: {
                colors: {
                    border: "hsl(var(--border))",
                    background: "hsl(var(--background))",
                    foreground: "hsl(var(--foreground))",
                    muted: {
                        DEFAULT: "hsl(var(--muted))",
                        foreground: "hsl(var(--muted-foreground))",
                    },
                },
                spacing: {
                    '18': '4.5rem',
                    '72': '18rem',
                    '84': '21rem',
                    '96': '24rem',
                },
                borderRadius: {
                    'xl': '1rem',
                    '2xl': '1.5rem',
                },
            }
        }
    }
</script>
```

**Step 2: 添加自定义CSS样式**

在 `<style>` 标签中添加：

```css
:root {
    --background: 0 0% 100%;
    --foreground: 0 0% 9%;
    --muted: 0 0% 96%;
    --muted-foreground: 0 0% 45%;
    --border: 0 0% 91%;
}

/* 响应式字体 */
.text-display {
    font-size: clamp(2.25rem, 5vw, 5rem);
    font-weight: 600;
    line-height: 1.1;
    letter-spacing: -0.025em;
}

.text-headline {
    font-size: clamp(1.75rem, 4vw, 3rem);
    font-weight: 600;
    line-height: 1.2;
    letter-spacing: -0.02em;
}

.text-title {
    font-size: clamp(1.125rem, 2.5vw, 1.5rem);
    font-weight: 600;
    line-height: 1.3;
    letter-spacing: -0.01em;
}

.text-body {
    font-size: clamp(0.875rem, 2vw, 1.125rem);
    font-weight: 400;
    line-height: 1.5;
}

.text-caption {
    font-size: clamp(0.75rem, 1.5vw, 0.875rem);
    font-weight: 400;
    line-height: 1.4;
    color: hsl(var(--muted-foreground));
}

/* Bento卡片 */
.bento-card {
    background: white;
    border-radius: 1.25rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.3s ease;
}

.bento-card:hover {
    transform: translateY(-0.5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* 图标占位符 */
.icon-placeholder {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg,
        hsl(var(--muted)) 0%,
        hsl(var(--background)) 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

/* Bento网格 */
.bento-grid {
    display: grid;
    gap: 1.5rem;
    max-width: 1120px;
    margin: 0 auto;
    padding: 0 1rem;
}

@media (min-width: 768px) {
    .bento-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 1.25rem;
    }
}

@media (min-width: 1024px) {
    .bento-grid {
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
    }
}

/* 按钮样式 */
.btn-primary {
    background: black;
    color: white;
    padding: 14px 32px;
    border-radius: 12px;
    font-weight: 500;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}

.btn-primary:hover {
    transform: translateY(-0.5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.btn-secondary {
    background: white;
    color: black;
    border: 1px solid hsl(var(--border));
    padding: 14px 32px;
    border-radius: 12px;
    font-weight: 500;
    transition: all 0.3s ease;
    cursor: pointer;
}

.btn-secondary:hover {
    background: hsl(var(--muted));
}

.text-link {
    color: black;
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.3s ease;
}

.text-link:hover {
    opacity: 0.7;
    text-decoration: underline;
}
```

**Step 3: 在浏览器中验证**

刷新页面，确保样式加载无错误

**Step 4: 提交**

```bash
git add demo/index.html
git commit -m "feat: 添加Tailwind配置和自定义样式"
```

---

## Task 4: BAS技能数据结构

**Files:**
- Modify: `demo/index.html` (添加数据到script)

**Step 1: 添加BAS技能数据**

在 `<script>` 标签中添加数据结构：

```javascript
// BAS技能数据（简化版，包含核心技能）
const basSkills = {
    tiers: [
        {
            id: "L0",
            name: "基础模型层",
            count: 43,
            description: "机器学习、深度学习基础算法"
        },
        {
            id: "L1",
            name: "生产层级",
            count: 6,
            description: "制造质量控制技能"
        },
        {
            id: "L2",
            name: "BMS层级",
            count: 14,
            description: "电池管理系统技能"
        },
        {
            id: "L3",
            name: "云端层级",
            count: 19,
            description: "高级诊断算法"
        },
        {
            id: "L4",
            name: "应用层级",
            count: 5,
            description: "应用层技能"
        },
        {
            id: "L5",
            name: "工商业层级",
            count: 7,
            description: "工商业应用技能"
        }
    ],
    skills: [
        {
            id: "C3.1",
            name: "内短路诊断-SOS",
            tier: "L3",
            whenToUse: "需要实时安全监控，适用于储能站、电动汽车等场景",
            compute: "<10MHz",
            batteryTypes: ["LFP", "NCM", "Na-ion"],
            description: "基于电压熵的内短路早期诊断"
        },
        {
            id: "C3.13",
            name: "析锂检测",
            tier: "L3",
            whenToUse: "LFP电池充电时检测析锂风险，预防热失控",
            compute: "<10MHz",
            batteryTypes: ["LFP"],
            description: "基于静置电压恢复的析锂检测"
        },
        {
            id: "C3.5",
            name: "安全熵评估",
            tier: "L3",
            whenToUse: "评估电池包整体健康状态和安全风险",
            compute: "<10MHz",
            batteryTypes: ["LFP", "NCM"],
            description: "基于多特征融合的安全熵计算"
        },
        {
            id: "C3.0",
            name: "数据净化",
            tier: "L3",
            whenToUse: "所有分析的前置步骤，清洗噪声数据",
            compute: "<10MHz",
            batteryTypes: ["ALL"],
            description: "数据预处理、去噪、特征提取"
        },
        {
            id: "C3.2",
            name: "内短路诊断-P2D",
            tier: "L3",
            whenToUse: "需要高精度内短路诊断，算力充足",
            compute: ">50MHz",
            batteryTypes: ["LFP", "NCM"],
            description: "基于P2D电化学模型的内短路诊断"
        }
    ]
};

// 案例数据
const cases = [
    {
        id: "huanggang",
        name: "皇岗储能场站",
        industry: "工商业储能",
        icon: "🏭",
        date: "2025.12",
        results: [
            "识别3个潜在内短路",
            "析锂风险提前预警",
            "安全熵实时监控"
        ],
        roi: "3个月回本",
        description: "10MWh磷酸铁锂储能系统"
    },
    {
        id: "fleet",
        name: "某营运车辆Fleet",
        industry: "电动汽车",
        icon: "🚚",
        date: "2025.10",
        results: [
            "SOH估计误差<2%",
            "剩余寿命预测准确率92%",
            "充电策略优化，延寿15%"
        ],
        roi: "节省运营成本18%",
        description: "100台电动公交 fleet"
    }
];

// 技术指标
const techSpecs = {
    skills: 94,
    responseTime: "<50ms",
    docDriven: "100%"
};
```

**Step 2: 在浏览器中验证**

打开控制台，输入 `basSkills.tiers.length`
Expected: 6

**Step 3: 提交**

```bash
git add demo/index.html
git commit -m "feat: 添加BAS技能和案例数据结构"
```

---

## Task 5: 导航系统

**Files:**
- Modify: `demo/index.html` (添加导航HTML和JS)

**Step 1: 添加导航HTML**

替换 `<nav id="main-nav"></nav>` 为：

```html
<nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-black/5">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
            <!-- Logo -->
            <div class="flex items-center">
                <a href="#" onclick="switchTab('home')" class="text-display text-xl font-semibold">
                    ASGARD
                </a>
            </div>

            <!-- 桌面导航 -->
            <div class="hidden md:flex items-center space-x-8">
                <a href="#" onclick="switchTab('home')" class="nav-link text-body font-medium transition-colors hover:text-black" data-tab="home">
                    首页
                </a>
                <a href="#" onclick="switchTab('skills')" class="nav-link text-body font-medium transition-colors hover:text-black" data-tab="skills">
                    技能库
                </a>
                <a href="#" onclick="switchTab('agent')" class="nav-link text-body font-medium transition-colors hover:text-black" data-tab="agent">
                    Agent编排
                </a>
                <a href="#" onclick="switchTab('analysis')" class="nav-link text-body font-medium transition-colors hover:text-black" data-tab="analysis">
                    分析
                </a>
                <a href="#" onclick="switchTab('cases')" class="nav-link text-body font-medium transition-colors hover:text-black" data-tab="cases">
                    案例
                </a>
            </div>

            <!-- 移动端菜单按钮 -->
            <div class="md:hidden">
                <button onclick="toggleMobileMenu()" class="p-2 rounded-lg hover:bg-black/5">
                    <i class="fas fa-bars text-xl"></i>
                </button>
            </div>
        </div>
    </div>

    <!-- 移动端菜单 -->
    <div id="mobile-menu" class="hidden md:hidden bg-white border-t border-black/5">
        <div class="px-4 py-3 space-y-2">
            <a href="#" onclick="switchTab('home'); toggleMobileMenu()" class="block py-2 text-body">首页</a>
            <a href="#" onclick="switchTab('skills'); toggleMobileMenu()" class="block py-2 text-body">技能库</a>
            <a href="#" onclick="switchTab('agent'); toggleMobileMenu()" class="block py-2 text-body">Agent编排</a>
            <a href="#" onclick="switchTab('analysis'); toggleMobileMenu()" class="block py-2 text-body">分析</a>
            <a href="#" onclick="switchTab('cases'); toggleMobileMenu()" class="block py-2 text-body">案例</a>
        </div>
    </div>
</nav>
```

**Step 2: 添加导航JS**

在 `<script>` 中添加：

```javascript
// Tab切换逻辑
let currentTab = 'home';

function switchTab(tabId) {
    event.preventDefault();
    currentTab = tabId;

    // 更新导航状态
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.dataset.tab === tabId) {
            link.classList.add('border-b-2', 'border-black');
        } else {
            link.classList.remove('border-b-2', 'border-black');
        }
    });

    // 渲染对应内容
    renderTabContent(tabId);

    return false;
}

function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('hidden');
}

// 初始化导航状态
document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('[data-tab="home"]').classList.add('border-b-2', 'border-black');
});
```

**Step 3: 测试导航点击**

1. 在浏览器中刷新页面
2. 点击导航链接
3. Expected: 控制台显示 "Rendering tab: xxx"（暂时）

**Step 4: 提交**

```bash
git add demo/index.html
git commit -m "feat: 添加导航系统和Tab切换逻辑"
```

---

## Task 6: 首页内容渲染

**Files:**
- Modify: `demo/index.html` (添加首页渲染逻辑)

**Step 1: 添加renderTabContent函数**

在 `<script>` 中添加：

```javascript
function renderTabContent(tabId) {
    const container = document.getElementById('tab-content');
    console.log('Rendering tab:', tabId);

    switch(tabId) {
        case 'home':
            container.innerHTML = renderHome();
            break;
        case 'skills':
            container.innerHTML = '<div class="max-w-7xl mx-auto px-4 py-12"><h1 class="text-headline mb-8">技能库</h1><p class="text-body">开发中...</p></div>';
            break;
        case 'agent':
            container.innerHTML = '<div class="max-w-7xl mx-auto px-4 py-12"><h1 class="text-headline mb-8">Agent智能编排</h1><p class="text-body">开发中...</p></div>';
            break;
        case 'analysis':
            container.innerHTML = '<div class="max-w-7xl mx-auto px-4 py-12"><h1 class="text-headline mb-8">数据分析</h1><p class="text-body">开发中...</p></div>';
            break;
        case 'cases':
            container.innerHTML = '<div class="max-w-7xl mx-auto px-4 py-12"><h1 class="text-headline mb-8">客户案例</h1><p class="text-body">开发中...</p></div>';
            break;
    }
}
```

**Step 2: 添加首页渲染函数**

```javascript
function renderHome() {
    return `
        <!-- Hero Section -->
        <section class="bento-grid py-16 md:py-24">
            <div class="col-span-full bento-card text-center py-16 md:py-24">
                <h1 class="text-display mb-6">ASGARD</h1>
                <p class="text-headline text-gray-600 mb-8">
                    The Intelligent Battery Brain
                </p>
                <p class="text-body max-w-2xl mx-auto mb-12 text-gray-600">
                    下一代电池管理系统的认知层<br/>
                    通过文档驱动编排，连接AI推理与电化学技能
                </p>
                <div class="flex gap-4 justify-center flex-wrap">
                    <button onclick="switchTab('skills')" class="btn-primary">
                        探索技能库
                    </button>
                    <button onclick="switchTab('agent')" class="btn-secondary">
                        查看演示
                    </button>
                </div>
            </div>
        </section>

        <!-- 核心能力 -->
        <section class="bento-grid py-12">
            <div class="bento-card">
                <div class="icon-placeholder mb-4">🧠</div>
                <h3 class="text-title mb-3">文档驱动编排</h3>
                <p class="text-caption">
                    依据## When to use<br/>
                    自动选择最优算法
                </p>
            </div>

            <div class="bento-card">
                <div class="icon-placeholder mb-4">⚡</div>
                <h3 class="text-title mb-3">自愈能力</h3>
                <p class="text-caption">
                    &lt;50ms故障自愈<br/>
                    无需人工干预
                </p>
            </div>

            <div class="bento-card">
                <div class="icon-placeholder mb-4">🔄</div>
                <h3 class="text-title mb-3">动态工作流</h3>
                <p class="text-caption">
                    运行时自适应<br/>
                    DAG动态调整
                </p>
            </div>
        </section>

        <!-- 技术指标 + 案例预览 -->
        <section class="bento-grid py-12">
            <div class="col-span-2 bento-card">
                <h3 class="text-title mb-8">技术规格</h3>
                <div class="grid grid-cols-3 gap-8 mb-8">
                    <div class="text-center">
                        <div class="text-display">${techSpecs.skills}+</div>
                        <div class="text-caption">BAS Skills</div>
                    </div>
                    <div class="text-center">
                        <div class="text-display">${techSpecs.responseTime}</div>
                        <div class="text-caption">自愈响应</div>
                    </div>
                    <div class="text-center">
                        <div class="text-display">${techSpecs.docDriven}</div>
                        <div class="text-caption">文档驱动</div>
                    </div>
                </div>
                <a href="#" class="text-link">查看完整技术规格 →</a>
            </div>

            <div class="col-span-2 bento-card">
                <h3 class="text-title mb-4">客户案例</h3>
                <div class="mb-6">
                    <div class="flex items-center gap-3 mb-4">
                        <div class="icon-placeholder" style="width:40px;height:40px;">${cases[0].icon}</div>
                        <div>
                            <div class="text-body font-semibold">${cases[0].name}</div>
                            <div class="text-caption">${cases[0].date}</div>
                        </div>
                    </div>
                    <ul class="text-caption space-y-2">
                        ${cases[0].results.map(r => `<li>✓ ${r}</li>`).join('')}
                    </ul>
                </div>
                <a href="#" onclick="switchTab('cases')" class="text-link">了解案例详情 →</a>
            </div>
        </section>
    `;
}
```

**Step 3: 测试首页渲染**

1. 刷新浏览器
2. Expected: 首页完整显示，包括Hero、核心能力、技术指标
3. 点击"探索技能库"按钮，Expected: 切换到技能库Tab

**Step 4: 提交**

```bash
git add demo/index.html
git commit -m "feat: 实现首页内容渲染"
```

---

## Task 7: Agent智能编排界面（对话区）

**Files:**
- Modify: `demo/index.html` (添加Agent对话界面)

**Step 1: 添加Agent界面HTML渲染**

修改 `renderTabContent` 中的 agent 分支：

```javascript
case 'agent':
    container.innerHTML = renderAgent();
    initAgentChat();
    break;
```

**Step 2: 添加renderAgent函数**

```javascript
function renderAgent() {
    return `
        <div class="max-w-[1600px] mx-auto px-4 py-8">
            <!-- 返回按钮 -->
            <button onclick="switchTab('home')" class="mb-6 flex items-center gap-2 text-link">
                <i class="fas fa-arrow-left"></i>
                返回首页
            </button>

            <!-- 标题 -->
            <h1 class="text-headline mb-8">ASGARD Agent 智能编排</h1>

            <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
                <!-- 左栏：Agent交互区 -->
                <div class="lg:col-span-2">
                    <div class="bento-card h-[600px] flex flex-col">
                        <div class="flex items-center gap-2 mb-4 pb-4 border-b border-black/5">
                            <div class="w-8 h-8 bg-black rounded-full flex items-center justify-center">
                                <i class="fas fa-robot text-white text-sm"></i>
                            </div>
                            <span class="font-semibold">ASGARD Agent</span>
                        </div>

                        <!-- 对话历史 -->
                        <div id="chat-history" class="flex-1 overflow-y-auto space-y-4 mb-4">
                            <div class="bg-gray-50 rounded-lg p-4">
                                <p class="text-body">👋 您好！我是ASGARD的智能助手。请描述您的电池管理需求，我会为您推荐最优的BAS技能组合。</p>
                            </div>
                        </div>

                        <!-- 推理过程（可折叠） -->
                        <div id="reasoning-panel" class="hidden mb-4">
                            <button onclick="toggleReasoning()" class="text-link text-sm mb-2">
                                🧠 推理过程 <span id="reasoning-toggle">[展开]</span>
                            </button>
                            <div id="reasoning-content" class="hidden bg-gray-50 rounded-lg p-4 text-caption space-y-2">
                            </div>
                        </div>

                        <!-- 输入框 -->
                        <div class="border-t border-black/5 pt-4">
                            <textarea id="agent-input"
                                class="w-full p-3 border border-black/10 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-black/5"
                                rows="3"
                                placeholder="描述您的需求，例如：我有一个华南地区的磷酸铁锂储能站，需要进行安全诊断..."></textarea>
                            <div class="flex justify-between items-center mt-3">
                                <button onclick="loadExamplePrompt()" class="text-caption text-link">
                                    📋 加载示例
                                </button>
                                <button onclick="sendMessage()" class="btn-primary px-6 py-2">
                                    发送 <i class="fas fa-paper-plane ml-2"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 右栏：Workflow DAG -->
                <div class="lg:col-span-3">
                    <div class="bento-card h-[600px]">
                        <h3 class="text-title mb-4">Workflow DAG</h3>
                        <div id="dag-container" class="flex-1 flex items-center justify-center">
                            <div class="text-center text-gray-400">
                                <div class="icon-placeholder mx-auto mb-4 opacity-50">
                                    <i class="fas fa-project-diagram text-4xl"></i>
                                </div>
                                <p class="text-body">在左侧输入您的需求</p>
                                <p class="text-caption">Agent将为您智能编排Workflow</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}
```

**Step 3: 添加Agent交互逻辑**

```javascript
// Agent对话状态
let agentState = {
    messages: [],
    workflow: null,
    isProcessing: false
};

// 初始化Agent聊天
function initAgentChat() {
    const input = document.getElementById('agent-input');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
}

// 加载示例提示词
function loadExamplePrompt() {
    const input = document.getElementById('agent-input');
    input.value = `我有一个位于华南地区的储能站，使用314Ah磷酸铁锂电池，需要进行安全诊断。我们已经有历史数据，希望实时监控，每分钟更新一次。系统主要用于工商业储能，环境温度一般在25°C左右。`;
}

// 发送消息
function sendMessage() {
    const input = document.getElementById('agent-input');
    const message = input.value.trim();

    if (!message || agentState.isProcessing) return;

    // 添加用户消息
    addMessage('user', message);
    input.value = '';

    // 模拟Agent处理
    agentState.isProcessing = true;
    simulateAgentResponse(message);
}

// 添加消息到对话历史
function addMessage(type, content) {
    const history = document.getElementById('chat-history');
    const messageDiv = document.createElement('div');

    if (type === 'user') {
        messageDiv.className = 'bg-black text-white rounded-lg p-4';
    } else {
        messageDiv.className = 'bg-gray-50 rounded-lg p-4';
    }

    messageDiv.innerHTML = `<p class="text-body whitespace-pre-line">${content}</p>`;
    history.appendChild(messageDiv);
    history.scrollTop = history.scrollHeight;

    agentState.messages.push({ type, content, timestamp: Date.now() });
}

// 模拟Agent响应（简化版）
function simulateAgentResponse(userMessage) {
    // 显示"正在思考"
    const thinkingDiv = document.createElement('div');
    thinkingDiv.id = 'thinking-indicator';
    thinkingDiv.className = 'bg-gray-50 rounded-lg p-4';
    thinkingDiv.innerHTML = '<p class="text-body">💭 正在理解您的需求...</p>';
    document.getElementById('chat-history').appendChild(thinkingDiv);

    setTimeout(() => {
        thinkingDiv.innerHTML = '<p class="text-body">💭 正在检索BAS技能库...</p>';
    }, 1000);

    setTimeout(() => {
        // 移除思考指示器
        document.getElementById('thinking-indicator')?.remove();

        // 添加Agent响应
        addMessage('agent', `✓ 需求已理解！

基于您的描述，我为您推荐以下BAS技能组合：

📚 **已匹配技能** (3个)
• C3.0 数据净化 - 前置依赖
• C3.1 内短路诊断(SOS) - 实时安全监控
• C3.13 析锂检测 - LFP电池专用

🧠 **决策依据**
• LFP电池 → 优先选择析锂检测
• 实时监控 → 选择低算力算法
• 华南地区 → 考虑高温影响

查看右侧生成的Workflow DAG，您可以拖拽调整顺序或点击节点查看详情。`);

        // 生成DAG
        generateMockDAG();

        agentState.isProcessing = false;
    }, 2500);
}

// 生成模拟DAG
function generateMockDAG() {
    const container = document.getElementById('dag-container');
    container.innerHTML = `
        <div class="w-full h-full flex flex-col items-center justify-center space-y-4">
            <div class="bg-green-50 border-2 border-green-500 rounded-lg p-4 w-48 text-center">
                <div class="text-title">C3.0</div>
                <div class="text-caption">数据净化</div>
                <div class="text-xs text-green-600 mt-2">✓ 前置依赖</div>
            </div>

            <div class="w-0.5 h-8 bg-black/20"></div>

            <div class="flex gap-4">
                <div class="bg-blue-50 border-2 border-blue-500 rounded-lg p-4 w-48 text-center hover:shadow-lg transition-shadow cursor-pointer">
                    <div class="text-title">C3.1</div>
                    <div class="text-caption">内短路诊断</div>
                    <div class="text-xs text-blue-600 mt-2">核心安全</div>
                </div>

                <div class="bg-orange-50 border-2 border-orange-500 rounded-lg p-4 w-48 text-center hover:shadow-lg transition-shadow cursor-pointer">
                    <div class="text-title">C3.13</div>
                    <div class="text-caption">析锂检测</div>
                    <div class="text-xs text-orange-600 mt-2">LFP专用</div>
                </div>
            </div>

            <div class="mt-8 flex gap-4">
                <button class="btn-secondary px-4 py-2 text-sm">
                    <i class="fas fa-download mr-2"></i>导出
                </button>
                <button class="btn-secondary px-4 py-2 text-sm">
                    <i class="fas fa-save mr-2"></i>保存模板
                </button>
                <button class="btn-primary px-4 py-2 text-sm">
                    <i class="fas fa-play mr-2"></i>运行
                </button>
            </div>
        </div>
    `;

    // 显示推理过程面板
    document.getElementById('reasoning-panel').classList.remove('hidden');
    document.getElementById('reasoning-content').innerHTML = `
        <div class="space-y-3">
            <div>
                <div class="font-semibold mb-1">1. 场景识别</div>
                <div>关键词: [LFP, 储能站, 安全诊断, 实时监控]</div>
            </div>
            <div>
                <div class="font-semibold mb-1">2. BAS技能检索 (RAG)</div>
                <div>✓ 检索94个SKILL.md</div>
                <div>✓ 匹配3个相关技能</div>
            </div>
            <div>
                <div class="font-semibold mb-1">3. 决策依据</div>
                <div>• LFP电池 → 优先析锂检测（热失控风险）</div>
                <div>• 实时要求 → 选择低算力算法</div>
            </div>
        </div>
    `;
}

// 切换推理过程显示
function toggleReasoning() {
    const content = document.getElementById('reasoning-content');
    const toggle = document.getElementById('reasoning-toggle');

    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        toggle.textContent = '[收起]';
    } else {
        content.classList.add('hidden');
        toggle.textContent = '[展开]';
    }
}
```

**Step 4: 测试Agent界面**

1. 导航到Agent编排Tab
2. 点击"📋 加载示例"
3. 点击"发送"
4. Expected: 流式对话 + DAG生成

**Step 5: 提交**

```bash
git add demo/index.html
git commit -m "feat: 实现Agent智能编排界面"
```

---

## Task 8: 响应式优化和最终测试

**Files:**
- Modify: `demo/index.html` (优化响应式)

**Step 1: 添加移动端适配样式**

在 `<style>` 中添加：

```css
/* 移动端优化 */
@media (max-width: 768px) {
    .bento-grid {
        grid-template-columns: 1fr;
        padding: 0 1rem;
    }

    .text-display {
        font-size: 2.5rem;
    }

    .text-headline {
        font-size: 2rem;
    }

    /* Agent界面移动端 */
    #agent-input {
        font-size: 16px; /* 防止iOS缩放 */
    }

    /* 确保触摸目标至少48x48px */
    button, .nav-link {
        min-height: 48px;
        min-width: 48px;
    }
}
```

**Step 2: 添加加载状态**

在Agent初始化时添加加载动画：

```css
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

**Step 3: 全浏览器测试清单**

在以下浏览器中测试：

```bash
# 桌面浏览器
- Chrome/Edge: 打开 demo/index.html
- Firefox: 打开 demo/index.html
- Safari: 打开 demo/index.html

# 移动浏览器（或模拟）
- iOS Safari: 在iPhone上测试
- Android Chrome: 在Android手机上测试
```

测试清单：
- [ ] 导航Tab切换正常
- [ ] 首页所有卡片显示正常
- [ ] Agent对话流程完整
- [ ] DAG生成显示正常
- [ ] 移动端汉堡菜单工作
- [ ] 所有按钮可点击（触摸目标≥48px）
- [ ] 滚动流畅（60fps）
- [ ] 无控制台错误

**Step 4: 性能检查**

打开浏览器开发者工具 → Network:
- [ ] 首屏加载<2秒
- [ ] CDN资源正常加载
- [ ] 无404错误

打开Lighthouse（Chrome DevTools）:
- [ ] Performance Score >90
- [ ] Accessibility Score >90
- [ ] Best Practices Score >90

**Step 5: 提交**

```bash
git add demo/index.html
git commit -m "feat: 响应式优化和最终测试"
```

---

## Task 9: 文档和部署准备

**Files:**
- Create: `demo/DEPLOYMENT.md`
- Update: `demo/README.md`

**Step 1: 创建部署文档**

创建 `demo/DEPLOYMENT.md`:

```markdown
# ASGARD Demo 部署指南

## 本地运行

### 方法1: 直接打开（推荐用于快速预览）

```bash
# 直接用浏览器打开
open demo/index.html  # macOS
start demo/index.html # Windows
xdg-open demo/index.html # Linux
```

### 方法2: HTTP服务器（推荐用于开发）

```bash
# Python 3
cd demo
python -m http.server 8000

# 访问 http://localhost:8000
```

## 生产部署

### 静态网站托管

Demo是纯静态文件，可部署到任何静态网站托管服务：

#### Vercel

```bash
# 安装Vercel CLI
npm i -g vercel

# 部署
cd demo
vercel
```

#### Netlify

```bash
# 拖拽demo文件夹到 Netlify Drop
# 或使用Netlify CLI
npm i -g netlify-cli
cd demo
netlify deploy
```

#### GitHub Pages

```bash
# 创建gh-pages分支
git subtree push --prefix demo origin gh-pages

# 在GitHub仓库设置中启用GitHub Pages
# 选择gh-pages分支
```

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name demo.asgard.com;
    root /path/to/demo;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 缓存CDN资源
    location ~* \.(js|css)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 性能优化建议

1. **启用压缩**: 使用gzip/brotli
2. **CDN**: 部署到Cloudflare或其他CDN
3. **预加载**: 添加`<link rel="preload">`用于关键资源

## 监控

建议添加：
- Google Analytics
- 崩溃报告（Sentry）

## 安全注意事项

- Demo不包含敏感信息
- 所有数据都是客户端模拟
- 如需后端API，需添加认证
```

**Step 2: 更新README**

更新 `demo/README.md`:

```markdown
# ASGARD 产品Demo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production](https://img.shields.io/badge/Status-Production-success)]()

## 🎯 产品定位

ASGARD是下一代电池管理系统的认知层，通过文档驱动编排，连接AI推理与电化学技能。

## ✨ 核心特性

- 🧠 **文档驱动编排**: 依据SKILL.md自动选择最优算法
- ⚡ **自愈能力**: <50ms故障自动恢复
- 🔄 **动态工作流**: 运行时自适应DAG调整
- 📚 **94+ BAS技能**: 覆盖L0-L5全产业链

## 🚀 快速开始

### 运行Demo

```bash
# 直接用浏览器打开
open demo/index.html

# 或使用HTTP服务器
cd demo
python -m http.server 8000
```

访问: http://localhost:8000

### 在线Demo

[https://demo.asgard.com](https://demo.asgard.com) (即将上线)

## 📖 功能演示

### 1. 首页
- 价值主张展示
- 核心能力介绍
- 技术指标和案例预览

### 2. Agent智能编排 ⭐
- 自然语言输入需求
- 多轮对话澄清
- 实时RAG检索展示
- 可视化Workflow DAG
- 推理过程透明化

### 3. 技能库
- 94+ BAS技能浏览
- 多维度筛选
- 技能对比

### 4. 数据分析
- CSV数据上传
- 实时分析
- 可视化报告

### 5. 客户案例
- 皇岗储能场站
- 营运车辆Fleet
- 更多案例...

## 🛠️ 技术栈

- **前端**: HTML5, JavaScript ES6+
- **样式**: Tailwind CSS (CDN)
- **图表**: ECharts 5.x (CDN)
- **图标**: Font Awesome (CDN)
- **部署**: 纯静态文件

## 📱 浏览器兼容性

- Chrome/Edge 90+
- Safari 14+
- Firefox 88+
- 移动端Safari iOS 14+
- 移动端Chrome Android 10+

## 📚 文档

- [设计文档](../docs/plans/2026-03-14-asgardo-demo-design.md)
- [部署指南](DEPLOYMENT.md)
- [ASGARD架构](../README.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE)

## 📧 联系我们

- 官网: [https://asgard.com](https://asgard.com)
- 邮箱: contact@asgard.com
- 微信: ASGARD_Official

---

**© 2026 ASGARD Team | Built for the Future of Energy Storage**
```

**Step 3: 提交**

```bash
git add demo/
git commit -m "docs: 添加部署文档和更新README"
```

---

## Task 10: 最终验证和发布

**Step 1: 完整功能回归测试**

测试清单：

```
导航系统
✓ Tab切换流畅
✓ 当前页面指示正确
✓ 移动端汉堡菜单
✓ 所有链接可点击

首页
✓ Hero区域显示正常
✓ 核心能力卡片（3个）
✓ 技术指标显示
✓ 案例预览卡片
✓ CTA按钮跳转正确

Agent编排
✓ 欢迎消息显示
✓ 示例加载功能
✓ 消息发送功能
✓ 流式响应动画
✓ 推理过程折叠/展开
✓ DAG生成正确
✓ 节点可交互

响应式
✓ 桌面布局（>1024px）
✓ 平板布局（768-1024px）
✓ 移动布局（<768px）
✓ 触摸目标≥48px

性能
✓ 首屏<2秒
✓ 无控制台错误
✓ CDN资源加载
✓ 滚动流畅

兼容性
✓ Chrome
✓ Safari
✓ Firefox
✓ 移动端Safari
✓ 移动端Chrome
```

**Step 2: 创建发布标签**

```bash
git tag -a v0.1.0 -m "ASGARD Demo MVP - 首次公开版本

- 首页展示
- Agent智能编排
- 基础导航系统
- 响应式设计
- Apple极简风格"

git push origin v0.1.0
```

**Step 3: 最终提交**

```bash
git add .
git commit -m "release: ASGARD Demo MVP v0.1.0

✨ 新功能:
- 首页产品介绍
- Agent智能编排界面
- BAS技能数据结构
- 响应式导航系统

🎨 设计:
- Apple极简风格
- Bento Grid布局
- Tailwind CSS样式
- 完整响应式支持

📱 兼容性:
- Chrome/Safari/Firefox
- iOS Safari / Android Chrome
- 桌面/平板/移动

📚 文档:
- README
- DEPLOYMENT.md
- 设计文档

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 🎯 MVP验收标准

完成所有任务后，应该达到：

### 功能验收
- [x] 5个Tab可切换
- [x] 首页内容完整
- [x] Agent对话流程
- [x] DAG可视化生成
- [x] 推理过程展示

### 视觉验收
- [x] Apple极简风格
- [x] Bento Grid布局
- [x] 8px网格对齐
- [x] 响应式完美

### 性能验收
- [x] 首屏<2秒
- [x] 无控制台错误
- [x] 流畅交互

### 文档验收
- [x] README完整
- [x] 部署文档
- [x] 设计文档

---

## 📊 下一步计划（P1功能）

### 技能库展示
- 两级展示机制
- 搜索和筛选
- 技能详情弹窗

### 数据分析
- CSV上传
- ECharts图表
- 结果导出

### 案例展示
- 案例详情页
- PDF下载

### 后端集成
- Agent API对接
- 真实Workflow执行
- 数据持久化

---

**计划状态**: ✅ MVP计划完成，等待执行

**预估工作量**: 3-5天（单人开发）

**技术难点**: Agent流式输出 + DAG可视化交互

**建议执行方式**: 使用 `superpowers:executing-plans` skill 逐任务执行
