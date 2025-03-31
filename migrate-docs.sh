#!/bin/bash

# This script migrates existing documentation to Docusaurus format

# Create necessary directories in the docs folder
mkdir -p docs/getting-started
mkdir -p docs/architecture
mkdir -p docs/development
mkdir -p docs/api-guide
mkdir -p docs/user-guide
mkdir -p docs/operations
mkdir -p docs/security
mkdir -p docs/contributing

# Copy existing documentation files
cp -R ../docs/getting-started/*.md docs/getting-started/ 2>/dev/null || :
cp -R ../docs/architecture/*.md docs/architecture/ 2>/dev/null || :
cp -R ../docs/development/*.md docs/development/ 2>/dev/null || :
cp -R ../docs/api/*.md docs/api-guide/ 2>/dev/null || :
cp -R ../docs/user-guide/*.md docs/user-guide/ 2>/dev/null || :
cp -R ../docs/operations/*.md docs/operations/ 2>/dev/null || :
cp -R ../docs/security/*.md docs/security/ 2>/dev/null || :
cp -R ../docs/contributing/*.md docs/contributing/ 2>/dev/null || :

# Copy testing documentation
mkdir -p docs/development/testing
cp -R ../docs/development/testing/*.md docs/development/testing/ 2>/dev/null || :
cp -R ../docs/testing/common/*.md docs/development/testing/ 2>/dev/null || :

# Update the sidebars.js file
cat > sidebars.js << 'SIDEBAR'
/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quickstart',
        'getting-started/configuration',
      ],
    },
    {
      type: 'category',
      label: 'Architecture',
      items: [
        'architecture/overview',
        'architecture/data-flow',
        'architecture/security',
      ],
    },
    {
      type: 'category',
      label: 'Development',
      items: [
        'development/setup',
        'development/coding-standards',
        'development/deployment',
        {
          type: 'category',
          label: 'Testing',
          items: [
            'development/testing/overview',
            'development/testing/unit-testing',
            'development/testing/integration-testing',
            'development/testing/e2e-testing',
            'development/testing/test-structure',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'API Guide',
      items: [
        'api-guide/overview',
        'api-guide/authentication',
        'api-guide/versioning',
      ],
    },
    {
      type: 'category',
      label: 'User Guide',
      items: [
        'user-guide/getting-started',
        'user-guide/troubleshooting',
      ],
    },
    {
      type: 'category',
      label: 'Operations',
      items: [
        'operations/monitoring',
        'operations/logging',
        'operations/backup',
        'operations/scaling',
      ],
    },
    {
      type: 'category',
      label: 'Security',
      items: [
        'security/overview',
        'security/authentication',
        'security/authorization',
        'security/compliance',
      ],
    },
    {
      type: 'category',
      label: 'Contributing',
      items: [
        'contributing/guidelines',
        'contributing/code-review',
        'contributing/release',
      ],
    },
  ],
};

module.exports = sidebars;
SIDEBAR

chmod +x migrate-docs.sh
echo "Migration script created: documentation/migrate-docs.sh"
