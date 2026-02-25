import React from 'react';
import Heading from '@theme/Heading';
import Section from '../Section';
import FeatureCard from '../FeatureCard';

export default function HomepageArchitecture() {
  return (
    <Section>
      <Heading as="h2" className="text--center margin-bottom--xl">
        Cloud-Native Architecture
      </Heading>

      <div className="row">
        <div className="col col--4">
          <FeatureCard
            title="KAgent"
            description="Intelligent agent orchestration and lifecycle management built for Kubernetes-native environments."
          />
        </div>

        <div className="col col--4">
          <FeatureCard
            title="KMCP Server"
            description="Model Context Protocol server responsible for deploying and managing specialized learning agents."
          />
        </div>

        <div className="col col--4">
          <FeatureCard
            title="AgentGateway"
            description="Security and audience validation layer protecting AI agent access and interactions."
          />
        </div>
      </div>
    </Section>
  );
}