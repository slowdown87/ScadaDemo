import React, { useEffect, useState } from 'react';
import { Card, Table, Tag, Button, Space, message, Badge } from 'antd';
import { CheckOutlined, DeleteOutlined } from '@ant-design/icons';
import { useCIPStore } from '@/store';
import type { AlarmInfo } from '@/types';
import { alarmApi } from '@/services';
import './AlarmPage.css';

const AlarmPage: React.FC = () => {
  const { alarms, fetchAlarms } = useCIPStore();
  const [loading] = useState(false);

  useEffect(() => {
    fetchAlarms();
  }, [fetchAlarms]);

  const handleAcknowledge = async (alarmId: number) => {
    try {
      const success = await alarmApi.ackAlarm(alarmId, 'Operator');
      if (success) {
        message.success('报警已确认');
        fetchAlarms();
      }
    } catch {
      message.error('确认失败');
    }
  };

  const handleClear = (_alarmId: number) => {
    message.info('清除报警功能开发中');
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'L0':
        return 'red';
      case 'L1':
        return 'orange';
      case 'L2':
        return 'yellow';
      default:
        return 'default';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return <Badge status="error" text="活跃" />;
      case 'ACKED':
        return <Badge status="warning" text="已确认" />;
      case 'CLEARED':
        return <Badge status="default" text="已清除" />;
      default:
        return status;
    }
  };

  const columns = [
    {
      title: '报警ID',
      dataIndex: 'alarm_id',
      key: 'alarm_id',
      width: 80,
    },
    {
      title: '等级',
      dataIndex: 'level',
      key: 'level',
      width: 80,
      render: (level: string) => (
        <Tag color={getLevelColor(level)}>{level}</Tag>
      ),
    },
    {
      title: '报警代码',
      dataIndex: 'alarm_code',
      key: 'alarm_code',
      width: 100,
    },
    {
      title: '报警内容',
      dataIndex: 'alarm_text',
      key: 'alarm_text',
    },
    {
      title: '区域',
      dataIndex: 'zone_name',
      key: 'zone_name',
      width: 100,
    },
    {
      title: '发生时间',
      dataIndex: 'trigger_time',
      key: 'trigger_time',
      width: 180,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusBadge(status),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: unknown, record: AlarmInfo) => (
        <Space>
          {record.status === 'ACTIVE' && (
            <Button
              size="small"
              type="primary"
              icon={<CheckOutlined />}
              onClick={() => handleAcknowledge(record.alarm_id)}
            >
              确认
            </Button>
          )}
          <Button
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleClear(record.alarm_id)}
          >
            清除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="alarm-page">
      <Card
        title="报警列表"
        extra={
          <Space>
            <Tag color="red">严重: {alarms.filter(a => a.level === 'L0').length}</Tag>
            <Tag color="orange">警告: {alarms.filter(a => a.level === 'L1').length}</Tag>
            <Tag color="yellow">提示: {alarms.filter(a => a.level === 'L2').length}</Tag>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={alarms}
          rowKey="alarm_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

export default AlarmPage;
