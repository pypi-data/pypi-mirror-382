import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';
import { motion } from 'framer-motion';
import ShimmerButton from '@site/src/components/AnimatedComponents/ShimmerButton';
import GradientText from '@site/src/components/AnimatedComponents/GradientText';
import CopyButton from '@site/src/components/AnimatedComponents/CopyButton';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero', styles.heroBanner)}>
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Heading as="h1" className="hero__title">
            <GradientText>{siteConfig.title}</GradientText>
          </Heading>
          <motion.p
            className="hero__subtitle"
            style={{fontSize: '1.5rem', marginBottom: '1rem'}}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            Memory-First Development for Claude Code
          </motion.p>
          <motion.p
            style={{fontSize: '1.1rem', maxWidth: '800px', margin: '0 auto 2rem', color: '#c9d1d9'}}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            Research. Plan. Implement. Commit.<br/>
            Build features faster with parallel sub-agents and persistent memory.
          </motion.p>
        </motion.div>

        <motion.div
          className={styles.buttons}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
        >
          <ShimmerButton href="/mem8/docs">
            Get Started →
          </ShimmerButton>
          <ShimmerButton
            href="https://github.com/killerapp/mem8"
            variant="outline"
          >
            View on GitHub
          </ShimmerButton>
        </motion.div>

        <motion.div
          className={styles.installCodeContainer}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center', maxWidth: '600px', margin: '0 auto' }}
        >
          <motion.div
            className={styles.installCode}
            whileHover={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 400, damping: 10 }}
          >
            <code>uvx mem8 init</code>
            <CopyButton text="uvx mem8 init" />
          </motion.div>
          <motion.p
            style={{ fontSize: '0.85rem', color: '#7d8590', marginTop: '0.5rem', textAlign: 'center' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.0, duration: 0.6 }}
          >
            Run in any git repository to set up mem8 workspace with Claude Code integration
          </motion.p>
        </motion.div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
