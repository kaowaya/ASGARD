# 运维报告模板设计

## 1. 报告结构

### 1.1 封面页
```
+----------------------------------------+
|           [公司Logo]                   |
|                                        |
|      储能场站运维报告                   |
|                                        |
|    报告类型：日报/周报/月报/年报        |
|    报告周期：YYYY-MM-DD ~ YYYY-MM-DD    |
|    生成时间：YYYY-MM-DD HH:MM:SS        |
|                                        |
+----------------------------------------+
```

### 1.2 目录页
- 运行概况
- 性能分析
- 告警统计
- 经济效益
- 设备健康
- 维护建议

## 2. 模板设计

### 2.1 日报模板

#### 运行概况
| 指标 | 今日数值 | 昨日数值 | 变化 |
|------|----------|----------|------|
| 充电量 (MWh) | 12.5 | 11.8 | +5.9% |
| 放电量 (MWh) | 11.2 | 10.5 | +6.7% |
| 循环效率 (%) | 94.5 | 94.2 | +0.3% |
| 运行时长 (h) | 24 | 24 | 0% |

#### 性能曲线
- SOC变化曲线（24小时）
- 功率变化曲线（24小时）
- 温度变化曲线（24小时）

### 2.2 周报/月报模板

#### 趋势分析
- 周度/月度充放电量趋势
- 收益趋势
- SOH衰减趋势

#### 对比分析
- 环比：与上周/上月对比
- 同比：与去年同期对比
- 达成率：与目标值对比

### 2.3 年报模板

#### 年度总结
- 关键指标汇总表
- 重大事件回顾
- 亮点与不足

#### 投资分析
- 投资回报率
- 全生命周期成本
- 盈亏平衡分析

## 3. 图表设计

### 3.1 趋势图
```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(dates, energy_values, marker='o', linewidth=2)
plt.title('充放电量趋势', fontsize=16, fontweight='bold')
plt.xlabel('日期', fontsize=12)
plt.ylabel('电量 (MWh)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('energy_trend.png', dpi=300)
```

### 3.2 分布图
```python
plt.figure(figsize=(10, 6))
plt.pie(sizes, labels=labels, autopct='%1.1f%%',
        startangle=90, colors=['#1890ff', '#52c41a', '#faad14'])
plt.title('告警级别分布', fontsize=16)
plt.axis('equal')
plt.tight_layout()
plt.savefig('alarm_distribution.png', dpi=300)
```

### 3.3 热力图
```python
import seaborn as sns

plt.figure(figsize=(12, 8))
sns.heatmap(temperature_data, annot=True, fmt='.1f',
            cmap='RdYlGn_r', center=30)
plt.title('电池簇温度分布', fontsize=16)
plt.xlabel('电池模块', fontsize=12)
plt.ylabel('电池簇', fontsize=12)
plt.tight_layout()
plt.savefig('temperature_heatmap.png', dpi=300)
```

## 4. 样式规范

### 4.1 字体
- 标题：黑体，18-24pt
- 副标题：黑体，14-16pt
- 正文：宋体，10-12pt
- 表头：黑体，11pt
- 表文：宋体，10pt

### 4.2 颜色
- 主色：#1890ff（蓝色）
- 成功：#52c41a（绿色）
- 警告：#faad14（橙色）
- 错误：#f5222d（红色）
- 文本：#000000（黑色）

### 4.3 间距
- 页边距：2.54cm
- 段前段后：0.5行
- 表格行距：1.15倍

## 5. 数据表格

### 5.1 基础表格样式
```
+----------+----------+----------+
|  列标题1  |  列标题2  |  列标题3  |
+----------+----------+----------+
|  数据1   |  数据2   |  数据3   |
+----------+----------+----------+
|  数据4   |  数据5   |  数据6   |
+----------+----------+----------+
```

### 5.2 条件格式
- 数值>阈值：红色
- 数值<阈值：绿色
- 趋势上升：↑
- 趋势下降：↓

## 6. PDF生成

### 6.1 使用ReportLab
```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph

def create_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []

    # 添加标题
    title = Paragraph("储能场站运维报告", title_style)
    story.append(title)

    # 添加表格
    data = [['指标', '数值'],
            ['充电量', '12.5 MWh'],
            ['放电效率', '94.5%']]
    table = Table(data)
    story.append(table)

    doc.build(story)
```

### 6.2 使用WeasyPrint
```python
from weasyprint import HTML

def html_to_pdf(html_file, pdf_file):
    HTML(filename=html_file).write_pdf(pdf_file)
```

## 7. 自动化调度

### 7.1 定时任务
```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

# 每天早上8点生成日报
@scheduler.scheduled_job('cron', hour=8, minute=0)
def generate_daily_report():
    config = ReportConfig(
        report_period=ReportPeriod.DAILY,
        start_time=datetime.now() - timedelta(days=1),
        end_time=datetime.now()
    )
    generator = ReportGenerator(config)
    report = generator.generate_report()
    # 发送邮件...

scheduler.start()
```

### 7.2 邮件发送
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_report_email(recipients, pdf_file):
    msg = MIMEMultipart()
    msg['Subject'] = '储能场站运维报告'
    msg['To'] = ', '.join(recipients)

    # 添加附件
    with open(pdf_file, 'rb') as f:
        attachment = MIMEApplication(f.read())
        attachment.add_header('Content-Disposition',
                             'attachment',
                             filename=os.path.basename(pdf_file))
        msg.attach(attachment)

    # 发送
    smtp = smtplib.SMTP('smtp.server.com', 587)
    smtp.send_message(msg)
    smtp.quit()
```

## 8. 版本控制

### 8.1 报告版本
- 版本号：v1.0, v1.1, v2.0
- 修订记录：每次更新记录变更内容

### 8.2 模板版本
- 模板ID：template_v1.0
- 更新日期：YYYY-MM-DD
- 更新说明：具体改动内容
