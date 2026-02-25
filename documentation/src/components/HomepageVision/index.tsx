import React from 'react';
import Heading from '@theme/Heading';
import Section from '../Section';
import FeatureCard from '../FeatureCard';

export default function HomepageVision() {
  return (
    <Section>
      <div style={{ maxWidth: "900px", margin: "0 auto" }}>
        <Heading as="h2" className="text--center margin-bottom--lg">
          From Chatbots to Adaptive Agent Systems
        </Heading>

        <p className="text--center margin-bottom--lg">
          This platform dynamically deploys specialized learning agents 
          inside a governed Kubernetes cluster. Each agent evolves 
          alongside the learner.
        </p>

        <div className="row margin-top--lg">
          <div className="col col--6">
            <FeatureCard
              title="Personalized Adaptation"
              description="Agents analyze comprehension, adjust teaching style, and propose structured learning paths."
            />
          </div>

          <div className="col col--6">
            <FeatureCard
              title="Governed Execution"
              description="All agents operate under RBAC, audience validation, and strict non-destructive policies."
            />
          </div>
        </div>
      </div>
    </Section>
  );
}