import React from 'react';
import Heading from '@theme/Heading';

export default function HomepageSecurity() {
  return (
    <section className="padding-vert--xl hero hero--dark">
      <div className="container text--center">
        <Heading as="h2">Secure by Design</Heading>

        <ul className="margin-top--md col col--6 col--offset-3 text--left">
          <li>Audience-restricted MCP access</li>
          <li>RBAC enforced at cluster and agent level</li>
          <li>No destructive permissions</li>
          <li>Full observability via OpenTelemetry</li>
        </ul>
      </div>
    </section>
  );
}