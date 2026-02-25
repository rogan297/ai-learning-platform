import React from 'react';
import Layout from '@theme/Layout';

import HomepageHero from '../components/HomepageHero';
import HomepageVision from '../components/HomepageVision';
import HomepageWorkflow from '../components/HomepageWorkflow';
import HomepageArchitecture from '../components/HomepageArchitecture';
import HomepageSecurity from '../components/HomepageSecurity';
import HomepageCTA from '../components/HomepageCTA';

export default function Home() {
  return (
    <Layout
      title="Adaptive Learning Agents"
      description="Cloud-native AI infrastructure for adaptive learning agents">
      <HomepageHero />
      <main>
        <HomepageVision />
        <HomepageWorkflow />
        <HomepageArchitecture />
        <HomepageSecurity />
        <HomepageCTA />
      </main>
    </Layout>
  );
}