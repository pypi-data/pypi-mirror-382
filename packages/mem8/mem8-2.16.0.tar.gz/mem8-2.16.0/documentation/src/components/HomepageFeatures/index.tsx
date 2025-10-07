import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import AnimatedCard from '@site/src/components/AnimatedComponents/AnimatedCard';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: '🔍 Research with Parallel Sub-Agents',
    description: (
      <>
        <code>/research_codebase</code> spawns specialized agents to explore your code in parallel.
        Automated codebase analysis generates structured research documents with file references and architectural insights.
      </>
    ),
  },
  {
    title: '🤝 Team Collaboration with Shared Templates',
    description: (
      <>
        Share Claude Code prompts and sub-agents across your team using GitHub templates.
        Install from <code>killerapp/mem8-templates</code> or create your own.
        Standardize workflows and best practices organization-wide.
      </>
    ),
  },
  {
    title: '⚡ Implement with Full Context',
    description: (
      <>
        <code>/implement_plan</code> executes with full context of your research and design.
        Checkboxes track progress. <code>/commit</code> creates conventional commits.
        Ship features faster with memory-first development.
      </>
    ),
  },
];

function Feature({title, description}: FeatureItem, index: number) {
  return (
    <div className={clsx('col col--4')}>
      <AnimatedCard delay={index * 0.2}>
        <div className="text--center padding-horiz--md">
          <Heading as="h3">{title}</Heading>
          <p>{description}</p>
        </div>
      </AnimatedCard>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} index={idx} />
          ))}
        </div>
      </div>
    </section>
  );
}
