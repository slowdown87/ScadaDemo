import React, { useEffect, useState } from 'react';
import { Card, Table, DatePicker, Button, Space, Tag, message } from 'antd';
import { DownloadOutlined, SearchOutlined } from '@ant-design/icons';
import { batchApi } from '@/services';
import type { BatchRecord } from '@/types';
import dayjs from 'dayjs';
import './HistoryPage.css';

const { RangePicker } = DatePicker;

const HistoryPage: React.FC = () => {
  const [records, setRecords] = useState<BatchRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);

  const handleSearch = async () => {
    if (dateRange) {
      try {
        const [start, end] = dateRange;
        const data = await batchApi.getBatchRecords({
          start_time: start.toISOString(),
          end_time: end.toISOString(),
          limit: 100,
        });
        setRecords(data);
      } catch {
        message.error('查询失败');
      }
    }
  };

  useEffect(() => {
    const fetchRecords = async () => {
      setLoading(true);
      try {
        const data = await batchApi.getBatchRecords({ limit: 50 });
        setRecords(data);
      } catch {
        message.error('获取历史记录失败');
      } finally {
        setLoading(false);
      }
    };
    fetchRecords();
  }, []);

  const handleExport = () => {
    message.info('导出CSV文件');
  };

  const columns = [
    {
      title: '记录ID',
      dataIndex: 'record_id',
      key: 'record_id',
      width: 150,
    },
    {
      title: '区域',
      dataIndex: 'zone_name',
      key: 'zone_name',
    },
    {
      title: '配方',
      dataIndex: 'recipe_name',
      key: 'recipe_name',
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 180,
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
      width: 180,
    },
    {
      title: '总时长',
      dataIndex: 'total_time',
      key: 'total_time',
      width: 100,
      render: (time: number) => `${Math.floor(time / 60)}分钟`,
    },
    {
      title: '结果',
      dataIndex: 'result',
      key: 'result',
      width: 80,
      render: (result: boolean) => (
        <Tag color={result ? 'green' : 'red'}>
          {result ? '成功' : '失败'}
        </Tag>
      ),
    },
    {
      title: '最终电导率',
      dataIndex: 'final_conductivity',
      key: 'final_conductivity',
      width: 120,
      render: (val: number) => `${val} μS/cm`,
    },
    {
      title: '失败原因',
      dataIndex: 'fail_reason',
      key: 'fail_reason',
      render: (val: string | null) => val || '-',
    },
  ];

  return (
    <div className="history-page">
      <Card
        title="清洗历史记录"
        extra={
          <Space>
            <RangePicker onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])} />
            <Button icon={<SearchOutlined />} onClick={handleSearch}>
              查询
            </Button>
            <Button icon={<DownloadOutlined />} onClick={handleExport}>
              导出CSV
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={records}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

export default HistoryPage;
