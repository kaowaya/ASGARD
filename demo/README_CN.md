# ASGARD Demo 前端

[English](README.md) | [简体中文]

## 概述

ASGARD Demo 前端展示了ASGARD系统的智能电池分析能力。这个单页应用提供了BAS（Battery Analysis Skills，电池分析技能）编排、案例研究和实时数据分析的交互式演示。

## 功能特性

### 1. 首页 (Home)
- 产品介绍和价值主张
- 核心优势和竞争优势
- 行动召唤按钮
- 响应式bento-grid布局
- 性能指标展示

### 2. 技能库 (Skills Library)
- **6个层级**: L0-L5按复杂度组织
- **67+ BAS技能**: 完整的技能生态系统，涵盖：
  - L0: 基础工具
  - L1: 基础数据操作
  - L2: 单体电池诊断
  - L3: 多电池分析
  - L4: 车队级洞察
  - L5: 战略优化
- **三级导航**: 层级 → 技能 → 详情
- **交互式卡片**: 点击查看详细信息
- **筛选和搜索**: 快速发现技能

### 3. Agent编排 (Agent Orchestration)
- **交互式对话**: 自然语言界面描述分析需求
- **动态DAG**: 实时工作流可视化，节点-边缘图
- **智能规划**: 基于用户意图自动编排技能
- **示例提示**: 常见任务的快速开始场景
- **对话历史**: 完整上下文跟踪

### 4. 数据分析 (Data Analysis)
- **拖放上传**: 简单的数据导入（CSV、JSON）
- **交互式可视化**:
  - 电压-时间折线图（支持缩放）
  - 温度热力图（颜色渐变）
  - 风险雷达图（多维分析）
- **AI洞察**: 诊断总结和可执行建议
- **响应式图表**: 窗口调整时自动重绘

### 5. 案例研究 (Case Studies)
- **真实案例**:
  - 黄冈储能站（Huanggang ESS Station）
  - 车队管理（Fleet Vehicle Management）
- **技术细节**: 完整的DAG可视化和BAS采用计划
- **可追溯性**: 根因分析和可执行建议
- **性能指标**: 优化前后对比

## 截图

> *生产环境部署后将添加截图*

## 使用方法

### 本地开发

1. **克隆仓库**:
   ```bash
   git clone <repository-url>
   cd ASGARD/.worktrees/demo-frontend
   ```

2. **启动本地服务器**:
   ```bash
   # 使用Python 3
   python -m http.server 8000

   # 或使用Node.js
   npx serve demo

   # 或使用PHP
   php -S localhost:8000
   ```

3. **在浏览器中打开**:
   ```
   http://localhost:8000/
   ```

### 无服务器快速开始

直接在浏览器中打开 `demo/index.html` 文件。基本功能无需服务器。

### 导航

使用顶部导航栏切换5个主要部分：
- **首页** (Home) - 产品概述和价值主张
- **技能库** (Skills) - 探索6个层级的67+ BAS技能
- **Agent编排** (Planner) - 交互式编排对话界面
- **分析** (Analysis) - 上传并分析电池数据
- **案例** (Cases) - 真实案例研究及技术细节

## 技术栈

- **前端**: 纯HTML5 + JavaScript ES6+（无框架）
- **样式**: Tailwind CSS 3.4 (CDN)
- **图标**: Font Awesome 6.5 (CDN)
- **图表**: Apache ECharts 5.4 (CDN)
- **构建**: 无需构建（纯静态HTML）
- **打包**: 单文件架构，简化设计

## 浏览器支持

- ✓ Chrome 90+（推荐）
- ✓ Safari 14+
- ✓ Firefox 88+
- ✓ Edge 90+
- ✓ 移动浏览器（iOS Safari 14+、Chrome Mobile）
- ✓ 平板浏览器（iPad OS 14+、Android平板）

## 开发

### 文件结构
```
demo/
├── index.html          # 主应用（所有代码在一个文件中）
├── README.md           # 英文文档
├── README_CN.md        # 中文文档
└── DEPLOYMENT.md       # 部署指南
```

### 核心特性
- **零构建流程**: 无npm、无webpack、无打包
- **无依赖**: 所有库通过CDN加载
- **单文件架构**: HTML/CSS/JS全部在一个文件中
- **响应式设计**: 移动优先，使用Tailwind
- **可访问性**: ARIA标签、语义化HTML、键盘导航
- **性能优化**: 防抖处理器、懒加载

### 代码组织
- **HTML**: 语义化结构，每个功能独立section
- **CSS**: Tailwind工具类 + 自定义样式在`<style>`中
- **JavaScript**: 模块化函数，职责清晰分离
  - 状态管理（简单对象）
  - UI渲染（每个组件独立函数）
  - 事件处理（尽可能委托）
  - 图表初始化（ECharts实例）

## 性能

- **初始加载**: <2秒（CDN缓存）
- **Lighthouse分数**: 目标>90（性能、可访问性、最佳实践）
- **移动优化**: 触摸目标≥44px，可读字体≥16px
- **图表优化**: 防抖调整处理器（300ms）
- **包大小**: ~50KB（HTML + 内联CSS/JS）

## 可访问性

- **ARIA标签**: 所有交互元素正确标记
- **键盘导航**: 完整键盘支持（Tab、Enter、Space）
- **屏幕阅读器**: 语义化HTML和动态内容的实时区域
- **颜色对比**: 符合WCAG AA标准（文本4.5:1）
- **焦点指示**: 所有交互元素可见焦点状态

## 架构

### 单文件理念
遵循奥卡姆剃刀原则，本demo采用单文件架构：
- **简洁性**: 无构建工具，无依赖管理
- **可移植性**: 一个文件包含所有内容
- **可维护性**: 清晰的代码组织和注释
- **性能**: 零构建时间，即时部署

### 状态管理
基于简单对象的手动响应式状态：
```javascript
const state = {
  currentTab: 'home',
  selectedTier: null,
  selectedSkill: null,
  chatMessages: [],
  analysisData: null
};
```

### 组件架构
功能分解，职责清晰：
- `renderHome()`: 首页渲染
- `renderSkills()`: 技能库渲染
- `renderPlanner()`: Agent编排渲染
- `renderAnalysis()`: 数据分析渲染
- `renderCases()`: 案例研究渲染

## 故障排除

### 图表不显示
- 检查浏览器控制台的JavaScript错误
- 验证ECharts CDN可访问（检查网络标签）
- 确保容器div有明确的高度
- 尝试清除浏览器缓存

### 样式未加载
- 验证Tailwind CDN可访问
- 检查网络连接
- 尝试硬刷新（Ctrl+Shift+R / Cmd+Shift+R）

### 移动端显示问题
- 清除浏览器缓存
- 在隐身模式下测试
- 检查viewport meta标签是否存在
- 验证Tailwind配置中的响应式断点

## 未来增强

- [ ] 添加暗黑模式切换
- [ ] 实现真实后端API集成
- [ ] 添加更多图表类型（散点图、箱线图）
- [ ] 导出分析报告为PDF
- [ ] 多语言支持（除英文/中文外）
- [ ] PWA能力（离线支持）
- [ ] 技能库高级筛选

## 许可证

[指定许可证]

## 联系方式

[添加联系信息]

## 文档

- [实现计划](../docs/plans/2026-03-14-asgardo-demo-implementation.md)
- [设计文档](../docs/plans/2026-03-14-asgardo-demo-design.md)
- [部署指南](DEPLOYMENT.md)
