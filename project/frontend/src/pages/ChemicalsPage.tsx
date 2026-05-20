import React from 'react';
import { Card, Row, Col, Progress, Statistic, Tag } from 'antd';
import './ChemicalsPage.css';

const ChemicalsPage: React.FC = () => {

  const chemicalConfig = [
    {
      name: '碱液 (NaOH)',
      concentration: '2.0%',
      temperature: '85℃',
      tank: 'T-CP01',
      status: '正常',
      color: '#1890ff',
    },
    {
      name: '酸液 (HNO₃)',
      concentration: '1.0%',
      temperature: '60℃',
      tank: 'T-CP02',
      status: '正常',
      color: '#52c41a',
    },
    {
      name: '消毒液',
      concentration: '0.5%',
      temperature: '常温',
      tank: 'T-CP03',
      status: '正常',
      color: '#faad14',
    },
  ];

  return (
    <div className="chemicals-page">
      <Row gutter={16}>
        {chemicalConfig.map((chem, index) => (
          <Col span={8} key={index}>
            <Card className="chemical-card" title={chem.name}>
              <div className="chemical-header">
                <Tag color={chem.color}>{chem.status}</Tag>
                <span>罐: {chem.tank}</span>
              </div>
              <div className="chemical-content">
                <Statistic title="浓度" value={chem.concentration} />
                <Statistic title="温度" value={chem.temperature} />
              </div>
              <div className="chemical-progress">
                <Progress percent={75} status="active" />
                <span>液位: 75%</span>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Card title="清洗剂参数配置" style={{ marginTop: 16 }}>
        <p>配置清洗剂的浓度、温度、流量等参数</p>
      </Card>
    </div>
  );
};

export default ChemicalsPage;
