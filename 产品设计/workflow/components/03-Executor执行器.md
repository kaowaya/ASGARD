# Workflow Executor（工作流执行器）

> 核心组件：Workflow引擎的执行引擎
> 主要职责：训练BAS、执行推理、管理数据

---

## 概述

Workflow Executor负责Workflow的实际执行，包括BAS模型的训练、推理执行、数据管理和结果聚合。它是Workflow引擎的"执行层"，将抽象的Workflow DAG转化为具体的算法执行。

---

## 核心职责

1. **BAS训练**：基于客户数据训练个性化BAS模型
2. **模型推理**：执行训练好的BAS进行推理
3. **数据管理**：管理Workflow执行过程中的数据流
4. **结果聚合**：聚合多个BAS的输出结果
5. **模型缓存**：缓存训练好的模型以加速重复执行

---

## 执行流程

### 完整执行流程

```python
def execute_workflow(workflow_dag, execution_plan, customer_data):
    """
    Workflow执行主函数
    """
    # 初始化执行上下文
    context = {
        'customer_data': customer_data,
        'trained_models': {},
        'intermediate_results': {},
        'final_results': {}
    }

    # 按照拓扑序执行每个BAS
    FOR EACH skill IN workflow_dag.topological_order():
        # Step 1: 加载Skill模板
        skill_template = load_skill_template(skill.name)

        # Step 2: 训练个性化模型
        trained_model = train_skill(
            template=skill_template,
            data=customer_data,
            battery_type=skill.config.battery_type,
            hyperparameters=skill.config
        )

        # 缓存模型
        context['trained_models'][skill.id] = trained_model

        # Step 3: 准备输入数据
        input_data = prepare_input_data(skill, context)

        # Step 4: 模型推理
        result = execute_inference(trained_model, input_data)

        # Step 5: 保存中间结果
        context['intermediate_results'][skill.id] = result

        # Step 6: 传递给依赖的BAS
        pass_to_dependents(result, skill, workflow_dag, context)

    # 聚合最终结果
    final_results = aggregate_results(context)

    return final_results
```

---

## BAS训练器

### 训练流程

```python
def train_skill(template, data, battery_type, config):
    """
    BAS训练函数
    """
    # 加载预训练权重（如果存在）
    IF template.pretrained_weights:
        model = load_weights(template.pretrained_weights)
        log_info(f"加载预训练权重：{template.pretrained_weights}")
    ELSE:
        model = template.model_architecture
        log_info("使用模型架构：{template.model_architecture}")

    # 数据预处理
    processed_data = preprocess(data, battery_type)

    # 迁移学习（微调）
    tuned_model = fine_tune(
        model=model,
        data=processed_data,
        hyperparameters=config,
        epochs=config.epochs,
        learning_rate=config.lr,
        batch_size=config.batch_size
    )

    # 验证
    metrics = validate(tuned_model, processed_data.validation_set)

    log_info(f"训练完成 - 准确率：{metrics.accuracy:.2%}")

    # 保存模型
    model_metadata = {
        'skill_id': template.id,
        'battery_type': battery_type,
        'accuracy': metrics.accuracy,
        'trained_at': timestamp(),
        'hyperparameters': config.to_dict(),
        'data_hash': hash(processed_data)
    }

    save_model(tuned_model, metadata=model_metadata)

    return tuned_model
```

### 数据预处理

```python
def preprocess(data, battery_type):
    """
    数据预处理
    """
    # Step 1: 数据清洗
    cleaned_data = clean_data(data)

    # Step 2: 电池类型特定处理
    IF battery_type == 'LFP':
        processed_data = lfp_preprocessing(cleaned_data)
    ELIF battery_type == 'NCM':
        processed_data = ncm_preprocessing(cleaned_data)
    ELIF battery_type == 'Na-ion':
        processed_data = na_ion_preprocessing(cleaned_data)
    ELSE:
        processed_data = generic_preprocessing(cleaned_data)

    # Step 3: 特征工程
    features = extract_features(processed_data)

    # Step 4: 归一化
    normalized_features = normalize(features)

    # Step 5: 划分训练集/验证集/测试集
    train_set, val_set, test_set = split_data(
        normalized_features,
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15
    )

    return PreprocessedData(
        train_set=train_set,
        validation_set=val_set,
        test_set=test_set
    )
```

### 模型微调

```python
def fine_tune(model, data, hyperparameters, epochs, learning_rate, batch_size):
    """
    模型微调
    """
    # 设置优化器
    optimizer = Adam(
        lr=learning_rate,
        weight_decay=hyperparameters.weight_decay
    )

    # 设置损失函数
    criterion = get_loss_function(hyperparameters.loss_type)

    # 训练循环
    FOR epoch IN range(epochs):
        model.train()

        FOR batch IN data.train_set:
            # 前向传播
            outputs = model(batch.inputs)
            loss = criterion(outputs, batch.labels)

            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # 验证
        model.eval()
        val_loss = validate(model, data.validation_set, criterion)

        log_info(f"Epoch {epoch+1}/{epochs} - Train Loss: {loss.item():.4f}, Val Loss: {val_loss:.4f}")

        # Early Stopping
        IF val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            save_checkpoint(model, epoch)
        ELSE:
            patience_counter += 1
            IF patience_counter > hyperparameters.patience:
                log_info("Early stopping triggered")
                BREAK

    # 加载最佳模型
    model = load_checkpoint(model)

    return model
```

---

## 模型推理

### 推理执行

```python
def execute_inference(model, input_data):
    """
    模型推理
    """
    # 设置模型为评估模式
    model.eval()

    # 前向传播
    WITH torch.no_grad():
        IF isinstance(input_data, list):
            # 批量推理
            outputs = []
            FOR batch IN input_data:
                output = model(batch)
                outputs.append(output)
            result = aggregate_outputs(outputs)
        ELSE:
            # 单个推理
            result = model(input_data)

    # 后处理
    postprocessed_result = postprocess(result)

    return postprocessed_result
```

### 批量推理优化

```python
def batch_inference(model, input_data_list, batch_size=32):
    """
    批量推理
    """
    results = []

    # 分批处理
    FOR i IN range(0, len(input_data_list), batch_size):
        batch = input_data_list[i:i+batch_size]

        # 堆叠为批量张量
        batch_tensor = stack_batch(batch)

        # 批量推理
        batch_output = model(batch_tensor)

        # 拆分结果
        batch_results = split_batch(batch_output)

        results.extend(batch_results)

    return results
```

---

## 数据管理

### 数据流管理

```python
class DataManager:
    """
    数据管理器
    """
    def __init__(self):
        self.data_store = {}
        self.cache = LRUCache(maxsize=1000)

    def store(self, key, data):
        """
        存储数据
        """
        self.data_store[key] = data
        self.cache.put(key, data)

    def retrieve(self, key):
        """
        检索数据
        """
        # 先从缓存查找
        IF self.cache.contains(key):
            return self.cache.get(key)

        # 缓存未命中，从存储查找
        IF key IN self.data_store:
            data = self.data_store[key]
            self.cache.put(key, data)
            return data

        ELSE:
            raise KeyError(f"Data not found: {key}")

    def prepare_input_data(self, skill, context):
        """
        准备BAS输入数据
        """
        input_data = {}

        # 从原始数据获取
        FOR input_param IN skill.inputs:
            IF input_param.source == 'raw':
                input_data[input_param.name] = context['customer_data'][input_param.field]

            # 从其他BAS的输出获取
            ELIF input_param.source == 'skill_output':
                source_skill_id = input_param.source_skill
                output_field = input_param.output_field
                input_data[input_param.name] = context['intermediate_results'][source_skill_id][output_field]

        return input_data
```

### 数据传递

```python
def pass_to_dependents(result, skill, workflow_dag, context):
    """
    传递结果到依赖的BAS
    """
    # 找到依赖该BAS的所有下游BAS
    dependents = workflow_dag.get_dependents(skill.id)

    FOR dependent IN dependents:
        # 检查下游BAS是否准备好执行
        IF check_ready_to_execute(dependent, context):
            # 所有依赖都已满足，可以执行
            log_info(f"BAS {dependent.id} 准备执行")
```

---

## 结果聚合

### 聚合策略

```python
def aggregate_results(context):
    """
    聚合Workflow最终结果
    """
    # 获取Workflow DAG的终止节点（无输出的节点）
    terminal_nodes = get_terminal_nodes(context['workflow_dag'])

    aggregated_results = {}

    FOR node IN terminal_nodes:
        node_result = context['intermediate_results'][node.id]

        # 根据聚合类型处理
        IF node.aggregation_type == 'single':
            aggregated_results[node.id] = node_result

        ELIF node.aggregation_type == 'average':
            aggregated_results[node.id] = average(node_result)

        ELIF node.aggregation_type == 'weighted_sum':
            aggregated_results[node.id] = weighted_sum(
                node_result,
                node.weights
            )

        ELIF node.aggregation_type == 'voting':
            aggregated_results[node.id] = voting(node_result)

        ELIF node.aggregation_type == 'custom':
            aggregated_results[node.id] = node.custom_aggregation(node_result)

    return aggregated_results
```

### 多模型融合

```python
def ensemble_models(models_results, weights):
    """
    多模型融合
    """
    # 加权平均
    weighted_result = sum([
        result * weight
        for result, weight IN zip(models_results, weights)
    ])

    return weighted_result
```

---

## 模型缓存

### 缓存策略

```python
class ModelCache:
    """
    模型缓存
    """
    def __init__(self, cache_dir='.cache/models'):
        self.cache_dir = cache_dir
        self.cache_index = load_cache_index()

    def get(self, skill_id, battery_type, data_hash):
        """
        获取缓存的模型
        """
        cache_key = f"{skill_id}_{battery_type}_{data_hash}"

        IF cache_key IN self.cache_index:
            model_path = self.cache_index[cache_key]
            model = load_model(model_path)
            log_info(f"模型缓存命中：{cache_key}")
            return model
        ELSE:
            log_info(f"模型缓存未命中：{cache_key}")
            return None

    def put(self, skill_id, battery_type, data_hash, model):
        """
        缓存模型
        """
        cache_key = f"{skill_id}_{battery_type}_{data_hash}"
        model_path = f"{self.cache_dir}/{cache_key}.pkl"

        # 保存模型
        save_model(model, model_path)

        # 更新缓存索引
        self.cache_index[cache_key] = model_path
        save_cache_index(self.cache_index)

        log_info(f"模型已缓存：{cache_key}")
```

---

## 性能优化

### 1. 模型量化

```python
def quantize_model(model, quantization_type='int8'):
    """
    模型量化
    """
    # 动态量化
    IF quantization_type == 'dynamic':
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {torch.nn.Linear, torch.nn.Conv2d},
            dtype=torch.qint8
        )

    # 静态量化
    ELIF quantization_type == 'static':
        # 校准
        calibrate_model(model, calibration_data)
        quantized_model = torch.quantization.quantize_static(
            model,
            dtype=torch.qint8
        )

    return quantized_model
```

### 2. 模型剪枝

```python
def prune_model(model, sparsity=0.3):
    """
    模型剪枝
    """
    # L1正则化剪枝
    parameters_to_prune = []
    FOR name, module IN model.named_modules():
        IF isinstance(module, (torch.nn.Conv2d, torch.nn.Linear)):
            parameters_to_prune.append((module, 'weight'))

    # 全局剪枝
    torch.nn.utils.prune.global_unstructured(
        parameters_to_prune,
        pruning_method=torch.nn.utils.prune.L1Unstructured,
        amount=sparsity
    )

    return model
```

### 3. ONNX导出

```python
def export_to_onnx(model, onnx_path):
    """
    导出为ONNX格式
    """
    dummy_input = torch.randn(1, *model.input_shape)

    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=12,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output']
    )

    log_info(f"模型已导出为ONNX：{onnx_path}")
```

---

## 执行示例

### 示例：热失控预防Workflow执行

```python
# 1. 加载Workflow DAG
workflow_dag = load_workflow_dag('thermal_runaway_prevention')

# 2. 加载执行计划
execution_plan = load_execution_plan('thermal_runaway_prevention')

# 3. 准备客户数据
customer_data = load_customer_data('customer_001')

# 4. 执行Workflow
results = execute_workflow(
    workflow_dag=workflow_dag,
    execution_plan=execution_plan,
    customer_data=customer_data
)

# 5. 输出结果
print(json.dumps(results, indent=2))
```

**输出示例**：

```json
{
  "C3.4": {
    "fault_level": "L2",
    "abnormal_cells": [15, 27, 103],
    "shannon_entropy": 2.3
  },
  "C3.6": {
    "center_temperature": 48.5,
    "temperature_gradient": 6.2
  },
  "C3.1": {
    "isc_cells": [15],
    "leakage_current": 8.2,
    "risc": 150
  },
  "C3.2": {
    "thermal_runaway_probability": 0.15,
    "risk_level": "MODERATE"
  },
  "B2.7": {
    "action": "limit_current",
    "current_limit": 0.5,
    "priority": "HIGH"
  }
}
```

---

## 延伸阅读

- [Workflow Planner（规划器）](./01-Planner规划器.md)
- [Workflow Orchestrator（编排器）](./02-Orchestrator编排器.md)
- [Workflow Monitor（监控器）](./04-Monitor监控器.md)
- [执行模式详解](../execution-modes.md)
