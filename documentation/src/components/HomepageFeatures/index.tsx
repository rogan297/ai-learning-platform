import React from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Agentic Orchestration',
    description: (
      <>
        Powered by <strong>KAgent</strong> and <strong>KMCP</strong>. Automate the lifecycle 
        of specialized agents that adapt content depth and teaching styles 
        dynamically based on user evolution.
      </>
    ),
  },
  {
    title: 'Zero-Trust Governance',
    description: (
      <>
        Secure-by-design. Integration with <strong>Keycloak</strong> and <strong>AgentGateway</strong> 
        ensures that only authenticated users and approved audiences can access 
        the MCP servers.
      </>
    ),
  },
  {
    title: 'Cloud-Native Scale',
    description: (
      <>
        Built on <strong>Kubernetes</strong> and <strong>PostgreSQL</strong>. 
        Engineered for horizontal scalability, high availability, and 
        full observability via <strong>OpenTelemetry</strong>.
      </>
    ),
  },
];

function Feature({title, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}