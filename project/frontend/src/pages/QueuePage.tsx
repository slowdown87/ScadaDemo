import React from 'react';
import { Card, Table, Tag, Button, Space, Progress } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useCIPStore } from '@/store';
import './QueuePage.css';

const QueuePage: React.FC = () => {
  const { zones, systemStatus } = useCIPStore();

  const queueData = zones.map((zone, index) => ({
    key: zone.zone_id,
    queue_no: index + 1,
    zone_id: zone.zone_id,
    zone_name: zone.zone_name,
    status: zone.state,
    progress: Math.round((zone.current_step / 5) * 100),
  }));

  const columns = [
    {
      title: '队列号',
      dataIndex: 'queue_no',
      key: 'queue_no',
      width: 80,
    },
    {
      title: '区域',
      dataIndex: 'zone_name',
      key: 'zone_name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          IDLE: 'default',
          READY: 'blue',
          STEP_EXEC: 'green',
          PAUSE: 'orange',
          FAULT: 'red',
        };
        return <Tag color={colorMap[status] || 'default'}>{status}</Tag>;
      },
    },
    {
      title: '清洗进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 200,
      render: (progress: number) => <Progress percent={progress} size="small" />,
    },
    {
      title: '操作',
      key: 'action',
      render: () => (
        <Space>
          <Button size="small" danger icon={<DeleteOutlined />}>
            移出队列
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="queue-page">
      <Card
        title="清洗队列管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />}>
            添加到队列
          </Button>
        }
      >
        <div style={{ marginBottom: 16 }}>
          队列总数: {systemStatus?.queue_count || 0} | 当前活跃: {systemStatus?.active_zones || 0}
        </div>
        <Table
          columns={columns}
          dataSource={queueData}
          rowKey="zone_id"
          pagination={false}
        />
      </Card>
    </div>
  );
};

export default QueuePage;
