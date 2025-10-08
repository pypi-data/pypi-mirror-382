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
    title: '🧠 Context Window Management',
    description: (
      <>
        Persistent memory system for Claude Code with structured thoughts and searchable documentation.
        <code>/research_codebase</code> spawns parallel agents to explore your code efficiently.
        Keep AI context focused and relevant across long development sessions.
      </>
    ),
  },
  {
    title: '🤝 External Templates & Team Collaboration',
    description: (
      <>
        Share Claude Code prompts and workflows using <a href="/docs/external-templates">external templates</a>.
        Install from <code>killerapp/mem8-templates</code> or create your own.
        Standardize development practices across teams and organizations.
      </>
    ),
  },
  {
    title: '🔧 Toolbelt & Port Management',
    description: (
      <>
        Integrated toolbelt system for installing and managing development tools.
        Intelligent port conflict detection and resolution for local services.
        Streamline your development environment setup and maintenance.
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
