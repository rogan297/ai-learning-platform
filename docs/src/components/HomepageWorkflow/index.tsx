import React from 'react';
import Heading from '@theme/Heading';
import Section from '../Section';
import FeatureCard from '../FeatureCard';

export default function HomepageWorkflow() {
  return (
    <Section dark>
      <Heading as="h2" className="text--center margin-bottom--xl">
        How the System Works
      </Heading>

      <div className="row">
        <div className="col col--4">
          <FeatureCard
            title="1. Topic Selection"
            description="The user defines what they want to learn and the system analyzes scope and complexity."
          />
        </div>

        <div className="col col--4">
          <FeatureCard
            title="2. Agent Deployment"
            description="KMCP deploys a specialized learning agent through KAgent orchestration."
          />
        </div>

        <div className="col col--4">
          <FeatureCard
            title="3. Adaptive Evolution"
            description="The agent dynamically adjusts depth, pacing, and methodology."
          />
        </div>
      </div>
    </Section>
  );
}