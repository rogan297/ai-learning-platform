import React from 'react';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';

export default function HomepageCTA() {
  return (
    <section className="padding-vert--xl text--center">
      <div className="container">
        <Heading as="h2">Ready to explore the architecture?</Heading>

        <div className="margin-top--md">
          <Link
            className="button button--primary button--lg"
            to="/docs/introduction/whats-ai-learning-platform">
            Start with the Documentation
          </Link>
        </div>
      </div>
    </section>
  );
}