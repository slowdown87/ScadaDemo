import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Tag,
  Table,
  Button,
  Space,
  Typography,
  Spin,
  Alert,
  Tooltip,
  Divider,
} from 'antd';
import {
  SafetyOutlined,
  ThunderboltOutlined,
  ToolOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import {
  anomalyApi,
  maintenanceApi,
  optimizationApi,
  type AnomalyResult,
  type RULResult,
  type OptimizationResult,
} from '@/services';
import { useCIPStore } from '@/store';

const { Text } = Typography;

interface AIPanelProps {
  zoneId?: number;
}

const AIPanel: React.FC<AIPanelProps> = ({ zoneId = 1 }) => {
  const { zones } = useCIPStore();
  const [anomalyResult, setAnomalyResult] = useState<AnomalyResult | null>(null);
  const [rulResult, setRulResult] = useState<RULResult | null>(null);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const zone = zones.find((z) => z.zone_id === zoneId);

  const fetchAnomalyDetection = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await anomalyApi.detect(zoneId);
      setAnomalyResult(result);
    } catch {
      setError('异常检测服务暂时不可用');
    } finally {
      setLoading(false);
    }
  }, [zoneId]);

  const fetchRULPrediction = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const currentHealthScore = zone
        ? 1 - (zone.conductivity > 50 ? 0.3 : zone.conductivity > 30 ? 0.2 : 0.1)
        : 0.8;
      const result = await maintenanceApi.predictRUL(zoneId, `PUMP-Z${zoneId}`, {
        current_health_score: currentHealthScore,
        degradation_rate: 0.01
      });
      setRulResult(result);
    } catch {
      setError('RUL预测服务暂时不可用');
    } finally {
      setLoading(false);
    }
  }, [zoneId, zone]);

  const fetchOptimization = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await optimizationApi.getRecommendations(zoneId, 'efficiency');
      setOptimizationResult(result);
    } catch {
      setError('优化服务暂时不可用');
    } finally {
      setLoading(false);
    }
  }, [zoneId]);

  const fetchAllData = useCallback(async () => {
    await Promise.all([fetchAnomalyDetection(), fetchRULPrediction(), fetchOptimization()]);
  }, [fetchAnomalyDetection, fetchRULPrediction, fetchOptimization]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const getAlarmLevelColor = (level: string) => {
    switch (level) {
      case 'normal': return 'green';
      case 'warning': return 'orange';
      case 'error': return 'red';
      case 'critical': return 'red';
      default: return 'default';
    }
  };

  const getAlarmLevelIcon = (level: string) => {
    switch (level) {
      case 'normal': return <CheckCircleOutlined />;
      case 'warning': return <ExclamationCircleOutlined />;
      case 'error':
      case 'critical': return <WarningOutlined />;
      default: return null;
    }
  };

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'excellent': return '#52c41a';
      case 'good': return '#1890ff';
      case 'fair': return '#faad14';
      case 'poor': return '#fa8c16';
      case 'critical': return '#ff4d4f';
      default: return '#8c8c8c';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'green';
      case 'medium': return 'blue';
      case 'high': return 'orange';
      case 'critical': return 'red';
      default: return 'default';
    }
  };

  const detectorColumns = [
    { title: '检测器', dataIndex: 'key', key: 'key' },
    {
      title: '状态',
      dataIndex: 'is_anomaly',
      key: 'is_anomaly',
      render: (isAnomaly: boolean) => (
        <Tag color={isAnomaly ? 'red' : 'green'}>
          {isAnomaly ? '异常' : '正常'}
        </Tag>
      ),
    },
    {
      title: '分数',
      dataIndex: 'anomaly_score',
      key: 'anomaly_score',
      render: (score: number) => `${(score * 100).toFixed(1)}%`,
    },
    { title: '说明', dataIndex: 'message', key: 'message', ellipsis: true },
  ];

  const detectorData = anomalyResult
    ? Object.entries(anomalyResult.detector_results).map(([key, value]) => ({ key, ...value }))
    : [];

  return (
    <div className="ai-panel">
      {error && (
        <Alert message={error} type="warning" showIcon closable style={{ marginBottom: 16 }} />
      )}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <SafetyOutlined />
                异常检测
              </Space>
            }
            extra={
              <Tooltip title="刷新">
                <Button type="text" icon={<ReloadOutlined />} onClick={fetchAnomalyDetection} loading={loading} />
              </Tooltip>
            }
          >
            {loading && !anomalyResult ? (
              <div style={{ textAlign: 'center', padding: 40 }}><Spin size="large" /></div>
            ) : anomalyResult ? (
              <>
                <Statistic
                  title="综合评分"
                  value={anomalyResult.overall_score}
                  precision={2}
                  suffix="%"
                  valueStyle={{ color: anomalyResult.is_anomaly ? '#ff4d4f' : '#52c41a' }}
                />
                <div style={{ marginTop: 16 }}>
                  <Tag color={getAlarmLevelColor(anomalyResult.alarm_level)} icon={getAlarmLevelIcon(anomalyResult.alarm_level)}>
                    {anomalyResult.alarm_level.toUpperCase()}
                  </Tag>
                </div>
                <Divider />
                <Text type="secondary">{anomalyResult.message}</Text>
                {anomalyResult.is_anomaly && (
                  <div style={{ marginTop: 12 }}>
                    <Text type="warning">{anomalyResult.recommended_action}</Text>
                  </div>
                )}
              </>
            ) : (
              <Text type="secondary">暂无数据</Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <ToolOutlined />
                维护预测
              </Space>
            }
            extra={
              <Tooltip title="刷新">
                <Button type="text" icon={<ReloadOutlined />} onClick={fetchRULPrediction} loading={loading} />
              </Tooltip>
            }
          >
            {loading && !rulResult ? (
              <div style={{ textAlign: 'center', padding: 40 }}><Spin size="large" /></div>
            ) : rulResult ? (
              <>
                <Statistic
                  title="剩余使用寿命"
                  value={rulResult.rul_days}
                  suffix="天"
                  precision={1}
                  valueStyle={{ color: getHealthColor(rulResult.health_status) }}
                />
                <div style={{ marginTop: 8 }}>
                  <Text type="secondary">约 {rulResult.rul_hours.toFixed(0)} 小时</Text>
                </div>
                <Divider />
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text type="secondary">健康状态: </Text>
                    <Tag color={getHealthColor(rulResult.health_status)}>{rulResult.health_status.toUpperCase()}</Tag>
                  </div>
                  <div>
                    <Text type="secondary">维护优先级: </Text>
                    <Tag color={getPriorityColor(rulResult.maintenance_priority)}>{rulResult.maintenance_priority.toUpperCase()}</Tag>
                  </div>
                  <div>
                    <Text type="secondary">置信度: </Text>
                    <Text>{(rulResult.confidence * 100).toFixed(0)}%</Text>
                  </div>
                </Space>
                <Divider />
                <Text type="secondary" style={{ fontSize: 12 }}>{rulResult.recommendation}</Text>
              </>
            ) : (
              <Text type="secondary">暂无数据</Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <ThunderboltOutlined />
                参数优化
              </Space>
            }
            extra={
              <Tooltip title="刷新">
                <Button type="text" icon={<ReloadOutlined />} onClick={fetchOptimization} loading={loading} />
              </Tooltip>
            }
          >
            {loading && !optimizationResult ? (
              <div style={{ textAlign: 'center', padding: 40 }}><Spin size="large" /></div>
            ) : optimizationResult ? (
              <>
                <Statistic
                  title="预期改进"
                  value={optimizationResult.expected_improvement_percent}
                  suffix="%"
                  precision={1}
                  valueStyle={{ color: '#52c41a' }}
                />
                <div style={{ marginTop: 8 }}>
                  <Text type="secondary">置信度: {(optimizationResult.confidence * 100).toFixed(0)}%</Text>
                </div>
                <Divider />
                <Text strong>建议:</Text>
                <ul style={{ paddingLeft: 16, margin: '8px 0 0 0' }}>
                  {optimizationResult.recommendations.map((rec, index) => (
                    <li key={index}>
                      <Text style={{ fontSize: 12 }}>{rec}</Text>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <Text type="secondary">暂无数据</Text>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AIPanel;
