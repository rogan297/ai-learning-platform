import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

export default function HomepageHero() {
  return (
    <header className={clsx('hero hero--dark', styles.heroBanner)}>
      <div className="container text--center">
        <Heading as="h1" className="hero__title">
          Adaptive Learning Agents
          <br />
          <span className="text--primary">
            AI Infrastructure Built on Kubernetes
          </span>
        </Heading>

        <p className="hero__subtitle margin-top--md">
          Deploy governed, scalable, and secure intelligent agents 
          that evolve alongside each learner — powered by KAgent and KMCP.
        </p>
        <iframe
          width="100%"
          height="450"
          src="https://www.youtube.com/embed/C-1tWim-4tc"
          title="How to install the AI Learning platform"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowfullscreen>
        </iframe>
        <div className="margin-top--lg">
          <Link
            className="button button--primary button--lg"
            to="/docs/introduction/whats-ai-learning-platform">
            Explore Documentation
          </Link>

          <Link
            className="button button--secondary button--lg margin-left--md"
            to="/docs/core-concepts/architecture">
            Architecture Overview
          </Link>
        </div>
      </div>
    </header>
  );
}
