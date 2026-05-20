import React, { useEffect, useState } from 'react';
import { Table, Card, Button, Space, Tag, Tabs, message } from 'antd';
import { PlusOutlined, EditOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useCIPStore } from '@/store';
import type { RecipeInfo, RecipeStep } from '@/types';
import { recipeApi } from '@/services';
import './RecipePage.css';

const RecipePage: React.FC = () => {
  const { recipes, fetchRecipes, sendCommand } = useCIPStore();
  const [selectedRecipeId, setSelectedRecipeId] = useState<number | null>(null);
  const [recipeSteps, setRecipeSteps] = useState<RecipeStep[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRecipes();
  }, [fetchRecipes]);

  useEffect(() => {
    if (!selectedRecipeId) {
      return;
    }
    const loadRecipeDetail = async () => {
      setLoading(true);
      try {
        const detail = await recipeApi.getRecipe(selectedRecipeId);
        setRecipeSteps(detail.steps);
      } catch {
        message.error('获取配方详情失败');
        setRecipeSteps([]);
      } finally {
        setLoading(false);
      }
    };
    loadRecipeDetail();
  }, [selectedRecipeId]);

  const handleExecuteRecipe = async (recipeId: number, zoneId: number) => {
    try {
      const result = await recipeApi.executeRecipe(zoneId, recipeId);
      if (result.status === 'ok') {
        message.success('配方执行成功');
        await sendCommand(zoneId, 'START');
      }
    } catch {
      message.error('配方执行失败');
    }
  };

  const handleTabChange = (recipeId: string) => {
    setSelectedRecipeId(Number(recipeId));
  };

  const columns = [
    {
      title: '配方ID',
      dataIndex: 'recipe_id',
      key: 'recipe_id',
      width: 80,
    },
    {
      title: '配方名称',
      dataIndex: 'recipe_name',
      key: 'recipe_name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '步骤数',
      dataIndex: 'step_count',
      key: 'step_count',
      width: 80,
    },
    {
      title: '总时间',
      dataIndex: 'total_time',
      key: 'total_time',
      width: 100,
      render: (time: number) => `${Math.floor(time / 60)}分钟`,
    },
    {
      title: '状态',
      dataIndex: 'enable',
      key: 'enable',
      width: 80,
      render: (enable: boolean) => (
        <Tag color={enable ? 'green' : 'red'}>
          {enable ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: unknown, record: RecipeInfo) => (
        <Space>
          <Button
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleExecuteRecipe(record.recipe_id, 1)}
          >
            执行
          </Button>
          <Button size="small" icon={<EditOutlined />}>
            编辑
          </Button>
        </Space>
      ),
    },
  ];

  const stepColumns = [
    {
      title: '步骤',
      dataIndex: 'step_no',
      key: 'step_no',
      width: 60,
    },
    {
      title: '介质',
      dataIndex: 'media',
      key: 'media',
      width: 100,
    },
    {
      title: '时长(秒)',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
    },
    {
      title: '目标温度(℃)',
      dataIndex: 'temp_sp',
      key: 'temp_sp',
      width: 120,
    },
    {
      title: '目标流量(m³/h)',
      dataIndex: 'flow_sp',
      key: 'flow_sp',
      width: 130,
    },
    {
      title: '电导率上限',
      dataIndex: 'conductivity_max',
      key: 'conductivity_max',
      width: 100,
      render: (val: number | null) => val ?? '-',
    },
  ];

  const tabItems = recipes.map((recipe) => ({
    key: String(recipe.recipe_id),
    label: recipe.recipe_name,
    children: (
      <Table
        columns={stepColumns}
        dataSource={recipeSteps}
        rowKey="step_no"
        pagination={false}
        size="small"
        loading={loading && selectedRecipeId === recipe.recipe_id}
      />
    ),
  }));

  return (
    <div className="recipe-page">
      <Card
        title="清洗配方管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />}>
            新建配方
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={recipes}
          rowKey="recipe_id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Card title="配方步骤预览" style={{ marginTop: 16 }}>
        <Tabs
          activeKey={selectedRecipeId ? String(selectedRecipeId) : undefined}
          onChange={handleTabChange}
          items={tabItems}
        />
      </Card>
    </div>
  );
};

export default RecipePage;
