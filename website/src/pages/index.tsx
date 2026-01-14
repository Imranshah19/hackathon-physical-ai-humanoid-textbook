import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

/**
 * Feature item for the homepage
 */
interface FeatureItem {
  title: string;
  icon: string;
  description: string;
  link: string;
}

const FeatureList: FeatureItem[] = [
  {
    title: 'Module 1: ROS2 Foundations',
    icon: '🤖',
    description:
      'Master the Robot Operating System 2 (ROS2) including nodes, topics, services, actions, URDF, and lifecycle management.',
    link: '/module-1/',
  },
  {
    title: 'Module 2: Simulation & Digital Twins',
    icon: '🎮',
    description:
      'Build realistic simulations using Gazebo and Unity. Create digital twins with physics-accurate environments and sensor models.',
    link: '/module-2/',
  },
  {
    title: 'Module 3: Isaac & Reinforcement Learning',
    icon: '🧠',
    description:
      'Train humanoid locomotion policies using NVIDIA Isaac Sim and Isaac Gym. Master PPO, domain randomization, and sim-to-real transfer.',
    link: '/module-3/',
  },
  {
    title: 'Module 4: Vision-Language-Action',
    icon: '👁️',
    description:
      'Integrate vision-language models with robotic action. Build end-to-end systems that understand natural language commands.',
    link: '/module-4/',
  },
];

function Feature({title, icon, description, link}: FeatureItem) {
  return (
    <div className={clsx('col col--6')}>
      <Link to={link} className={styles.featureCard}>
        <div className={styles.featureIcon}>{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
      </Link>
    </div>
  );
}

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/module-1/">
            Start Learning
          </Link>
          <Link
            className="button button--outline button--lg"
            to="https://github.com"
            style={{marginLeft: '1rem', color: 'white', borderColor: 'white'}}>
            View on GitHub
          </Link>
        </div>
      </div>
    </header>
  );
}

function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

function HomepageAbout() {
  return (
    <section className={styles.about}>
      <div className="container">
        <div className="row">
          <div className="col col--8 col--offset-2">
            <h2>About This Textbook</h2>
            <p>
              This comprehensive textbook guides you through building intelligent
              humanoid robots from the ground up. Starting with ROS2 fundamentals,
              you'll progress through simulation, reinforcement learning, and
              cutting-edge vision-language-action models.
            </p>
            <h3>What You'll Learn</h3>
            <ul>
              <li>Build and program robots using ROS2 Humble</li>
              <li>Create high-fidelity simulations with Gazebo and Unity</li>
              <li>Train locomotion policies using NVIDIA Isaac</li>
              <li>Integrate VLMs for natural language robot control</li>
              <li>Deploy policies from simulation to real hardware</li>
            </ul>
            <h3>Prerequisites</h3>
            <ul>
              <li>Python programming experience</li>
              <li>Basic understanding of Linux command line</li>
              <li>Familiarity with machine learning concepts (helpful)</li>
              <li>GPU with CUDA support (for Isaac modules)</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="A comprehensive textbook for building intelligent humanoid robots with ROS2, simulation, and AI.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <HomepageAbout />
      </main>
    </Layout>
  );
}
