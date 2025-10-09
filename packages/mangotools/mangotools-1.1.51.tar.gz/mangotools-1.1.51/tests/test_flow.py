# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-09-26 18:13
# @Author : 毛鹏
import unittest
from mangotools.mangos import build_decision_tree, get_execution_order_with_config_ids


def find_flow_order(flow_data):
    # 构建邻接表和父节点记录
    adjacency = {}
    parent_count = {}

    # 初始化
    for node in flow_data.get('nodes'):
        node_id = node['id']
        adjacency[node_id] = []
        parent_count[node_id] = 0

        # 填充邻接表和父节点计数
    for edge in flow_data.get('edges'):
        source = edge['source']['node_id']
        target = edge['target']['node_id']
        adjacency[source].append(target)
        parent_count[target] += 1

    # 找到起始节点（没有父节点的节点）
    start_nodes = [node_id for node_id in parent_count if parent_count[node_id] == 0]

    # 深度优先搜索生成执行顺序
    execution_order = []
    visited = set()

    def dfs(node_id):
        if node_id not in visited:
            visited.add(node_id)
            execution_order.append(node_id)
            for child in adjacency.get(node_id, []):
                dfs(child)

    for node_id in start_nodes:
        dfs(node_id)

    return execution_order


class TestCache(unittest.TestCase):
    def setUp(self):
        """在每个测试方法前初始化"""
        with open('test-flow.json', 'r', encoding='utf-8') as f:
            import json
            self.data = json.load(f)

    def test_flow(self):
        """测试基本缓存操作"""
        # 测试设置和获取缓存
        data = build_decision_tree(self.data)
        print(data)

    def test_condition(self):
        # 获取执行顺序
        execution_order = find_flow_order(self.data)
        print("流程执行顺序（节点ID）：", execution_order)

        # 可选：按顺序输出节点标签
        print("\n流程执行顺序（节点标签）：")
        for node_id in execution_order:
            for node in nodes:
                if node['id'] == node_id:
                    print(f"- {node['label']} (ID: {node_id})")
                    break