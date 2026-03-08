# 储能大屏设计规范

## 1. 设计原则

### 1.1 可视化原则
- **一目了然**：关键指标突出显示
- **层次清晰**：重要信息优先级高
- **实时更新**：数据刷新及时
- **色彩协调**：配色专业舒适

### 1.2 布局原则
- **黄金分割**：重要区域放在视觉焦点
- **信息分组**：相关指标聚合显示
- **留白平衡**：避免信息过载
- **响应式设计**：适配不同屏幕

## 2. 配色方案

### 2.1 深色主题（推荐）
```css
--background: #0a0e27;
--card-background: #111a3e;
--primary-color: #1890ff;
--success-color: #52c41a;
--warning-color: #faad14;
--error-color: #f5222d;
--text-primary: #ffffff;
--text-secondary: #a6adb4;
```

### 2.2 浅色主题
```css
--background: #f0f2f5;
--card-background: #ffffff;
--primary-color: #1890ff;
--success-color: #52c41a;
--warning-color: #faad14;
--error-color: #f5222d;
--text-primary: #000000;
--text-secondary: #595959;
```

## 3. 图表规范

### 3.1 折线图
- 用途：趋势分析
- 颜色：主色调
- 线宽：2-3px
- 数据点：可选

### 3.2 柱状图
- 用途：对比分析
- 颜色：渐变色
- 间距：柱宽的20%

### 3.3 饼图
- 用途：占比分析
- 颜色：多色系
- 标签：显示百分比

### 3.4 仪表盘
- 用途：KPI展示
- 颜色：红黄绿三色
- 刻度：清晰标注

## 4. 组件库

### 4.1 数据卡片
```
+------------------+
| 图标  指标名称    |
|      123.45      |
|      单位         |
|  ▲ 12.5% 较昨日  |
+------------------+
```

### 4.2 告警列表
```
+------------------------+
| [严重] 告警内容  10:00 |
| [警告] 告警内容  09:30 |
+------------------------+
```

### 4.3 能量流图
```
    光伏
     |
     v
+---+---+
|  PCS  |---> 电网
+---+---+
     |
     v
   电池
```

## 5. 响应式布局

### 5.1 断点设计
- 4K (3840×2160)：完整布局
- 2K (2560×1440)：紧凑布局
- 1080p (1920×1080)：精简布局

### 5.2 组件适配
- 图表：随容器缩放
- 文字：相对单位（rem/em）
- 间距：百分比或vw/vh

## 6. 动画效果

### 6.1 过渡动画
- 时长：300-500ms
- 缓动：ease-in-out
- 触发：数据更新、页面切换

### 6.2 数字滚动
```javascript
function animateNumber(element, target, duration) {
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const current = Math.floor(start + (target - start) * progress);
        element.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}
```

## 7. 性能优化

### 7.1 渲染优化
- 虚拟滚动（长列表）
- Canvas渲染（大量数据点）
- 按需加载（非首屏组件）

### 7.2 数据优化
- 数据聚合（降低频率）
- 增量更新（只传变化）
- 缓存策略（减少请求）

## 8. 无障碍设计

### 8.1 色盲友好
- 不仅依赖颜色表达信息
- 使用图标+颜色组合
- 高对比度模式

### 8.2 键盘导航
- Tab键顺序合理
- 焦点状态清晰
- 快捷键支持
