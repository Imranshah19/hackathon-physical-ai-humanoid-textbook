import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Sidebar configuration for the Physical AI & Humanoid Robotics Textbook.
 *
 * The book is organized into 4 modules, each covering a major topic area.
 */
const sidebars: SidebarsConfig = {
  bookSidebar: [
    {
      type: 'doc',
      id: 'index',
      label: 'Home',
    },
    {
      type: 'doc',
      id: 'module-1/README',
      label: 'Module 1 Overview',
    },
    {
      type: 'category',
      label: 'Module 1: ROS2 Foundations',
      collapsed: false,
      items: [
        'module-1/chapters/ch01-ros2-foundations',
        'module-1/chapters/ch02-nodes-topics-messages',
        'module-1/chapters/ch03-services-actions',
        'module-1/chapters/ch04-urdf-xacro',
        'module-1/chapters/ch05-launch-parameters',
        'module-1/chapters/ch06-lifecycle-safety',
        'module-1/chapters/ch07-debugging-tools',
        {
          type: 'category',
          label: 'Exercises',
          items: [
            'module-1/exercises/README',
            'module-1/exercises/e2-1-multi-joint-publisher',
            'module-1/exercises/e3-1-trajectory-action',
            'module-1/exercises/e4-1-add-robot-hands',
            'module-1/exercises/e6-1-lifecycle-publisher',
            'module-1/exercises/e7-1-debug-challenge',
          ],
        },
      ],
    },
    {
      type: 'doc',
      id: 'module-2/README',
      label: 'Module 2 Overview',
    },
    {
      type: 'category',
      label: 'Module 2: Simulation & Digital Twins',
      collapsed: true,
      items: [
        'module-2/chapters/ch01-digital-twin-fundamentals',
        'module-2/chapters/ch02-gazebo-world-setup',
        'module-2/chapters/ch03-spawning-robots',
        'module-2/chapters/ch04-sensor-simulation',
        'module-2/chapters/ch05-physics-tuning',
        'module-2/chapters/ch06-unity-setup',
        'module-2/chapters/ch07-photorealistic-environments',
        'module-2/chapters/ch08-synthetic-sensor-data',
        'module-2/chapters/ch09-domain-randomization',
        'module-2/chapters/ch10-integration-debugging',
        {
          type: 'category',
          label: 'Exercises',
          items: [
            'module-2/exercises/ex01-gazebo-world',
            'module-2/exercises/ex02-robot-spawn',
            'module-2/exercises/ex03-sensor-fusion',
            'module-2/exercises/ex04-unity-vision',
            'module-2/exercises/ex05-full-integration',
          ],
        },
      ],
    },
    {
      type: 'doc',
      id: 'module-3/README',
      label: 'Module 3 Overview',
    },
    {
      type: 'category',
      label: 'Module 3: Isaac & Reinforcement Learning',
      collapsed: true,
      items: [
        'module-3/chapters/ch01-introduction-isaac',
        'module-3/chapters/ch02-isaac-sim-setup',
        'module-3/chapters/ch03-isaac-gym-fundamentals',
        'module-3/chapters/ch04-humanoid-environment',
        'module-3/chapters/ch05-reward-design',
        'module-3/chapters/ch06-ppo-training',
        'module-3/chapters/ch07-domain-randomization',
        'module-3/chapters/ch08-curriculum-learning',
        'module-3/chapters/ch09-policy-deployment',
        'module-3/chapters/ch10-sim-to-real',
        {
          type: 'doc',
          id: 'module-3/exercises/README',
          label: 'Exercises',
        },
      ],
    },
    {
      type: 'doc',
      id: 'module-4/README',
      label: 'Module 4 Overview',
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action',
      collapsed: true,
      items: [
        'module-4/chapters/ch01-introduction-vla',
        'module-4/chapters/ch02-vlm-foundations',
        'module-4/chapters/ch03-action-tokenization',
        'module-4/chapters/ch04-language-grounding',
        'module-4/chapters/ch05-vla-pipeline',
        'module-4/chapters/ch06-ros2-integration',
        'module-4/chapters/ch07-safety-constraints',
        'module-4/chapters/ch08-finetuning',
        'module-4/chapters/ch09-evaluation',
        'module-4/chapters/ch10-end-to-end-demo',
        {
          type: 'doc',
          id: 'module-4/exercises/README',
          label: 'Exercises',
        },
      ],
    },
  ],
};

export default sidebars;
