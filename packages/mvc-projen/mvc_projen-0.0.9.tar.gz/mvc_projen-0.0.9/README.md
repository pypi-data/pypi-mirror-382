![Source](https://img.shields.io/github/stars/MV-Consulting/mvc-projen?logo=github&label=GitHub%20Stars)
[![Build Status](https://github.com/MV-Consulting/mvc-projen/actions/workflows/build.yml/badge.svg)](https://github.com/MV-Consulting/mvc-projen/actions/workflows/build.yml)
[![ESLint Code Formatting](https://img.shields.io/badge/code_style-eslint-brightgreen.svg)](https://eslint.org)
[![Latest release](https://img.shields.io/github/release/MV-Consulting/mvc-projen.svg)](https://github.com/MV-Consulting/mvc-projen/releases)
![GitHub](https://img.shields.io/github/license/MV-Consulting/mvc-projen)
[![npm](https://img.shields.io/npm/dt/@mavogel/mvc-projen?label=npm&color=orange)](https://www.npmjs.com/package/@mavogel/mvc-projen)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@mavogel/mvc-projen)

# mvc-projen

The [projen](https://projen.io/) baseline for all [MV Consulting](https://manuel-vogel.de/) projects.

## Table of Contents

* [Features](#features)
* [Usage](#usage)
* [Inspiration](#inspiration)

## Features

* 📏 **Best Practice and unified Setup**: All the scaffolders we need are in one place and tested. From `cdk-constructs` to later `clis` with [golang](https://go.dev/)
* 🏗️ **Extensibility**: Pass in customized options for the scaffolder templates

## Usage

```bash
# 1. create a new project directory
mkdir my-new-construct &&  cd my-new-construct

# 2. set up the project using the projen new command
npx projen new \
    --from @mavogel/mvc-projen@~0 \
    --cdkVersion=2.177.0 \
    --package-manager=npm
```

## Inspiration

This project was created based on the following inspiration

* [taimos-projen](https://github.com/taimos/taimos-projen): code from [Thorsten Höger](https://www.taimos.de/) has always been an inspiration for my `cdk` and [projen](https://projen.io/) projects.
* [projen-cdk-hugo-pipeline](https://github.com/MV-Consulting/projen-cdk-hugo-pipeline/): a previous projen baseline we built, during which we learned a lot about the internal of projen. We could build up on this knowledge.

## 🚀 Unlock the Full Potential of Your AWS Cloud Infrastructure

Hi, I’m Manuel, an AWS expert passionate about empowering businesses with **scalable, resilient, and cost-optimized cloud solutions**. With **MV Consulting**, I specialize in crafting **tailored AWS architectures** and **DevOps-driven workflows** that not only meet your current needs but grow with you.

---


### 🌟 Why Work With Me?

✔️ **Tailored AWS Solutions:** Every business is unique, so I design custom solutions that fit your goals and challenges.
✔️ **Well-Architected Designs:** From scalability to security, my solutions align with AWS Well-Architected Framework.
✔️ **Cloud-Native Focus:** I specialize in modern, cloud-native systems that embrace the full potential of AWS.
✔️ **Business-Driven Tech:** Technology should serve your business, not the other way around.

---


### 🛠 What I Bring to the Table

🔑 **12x AWS Certifications**
I’m **AWS Certified Solutions Architect and DevOps – Professional** and hold numerous additional certifications, so you can trust I’ll bring industry best practices to your projects. Feel free to explose by [badges](https://www.credly.com/users/manuel-vogel)

⚙️ **Infrastructure as Code (IaC)**
With deep expertise in **AWS CDK** and **Terraform**, I ensure your infrastructure is automated, maintainable, and scalable.

📦 **DevOps Expertise**
From CI/CD pipelines with **GitHub Actions** and **GitLab CI** to container orchestration **Kubernetes** and others, I deliver workflows that are smooth and efficient.

🌐 **Hands-On Experience**
With over **7 years of AWS experience** and a decade in the tech world, I’ve delivered solutions for companies large and small. My open-source contributions showcase my commitment to transparency and innovation. Feel free to explore my [GitHub profile](https://github.com/mavogel)

---


### 💼 Let’s Build Something Great Together

I know that choosing the right partner is critical to your success. When you work with me, you’re not just contracting an engineer – you’re gaining a trusted advisor and hands-on expert who cares about your business as much as you do.

✔️ **Direct Collaboration**: No middlemen or red tape – you work with me directly.
✔️ **Transparent Process**: Expect open communication, clear timelines, and visible results.
✔️ **Real Value**: My solutions focus on delivering measurable impact for your business.

<a href="https://tinyurl.com/mvc-15min"><img alt="Schedule your call" src="https://img.shields.io/badge/schedule%20your%20call-success.svg?style=for-the-badge"/></a>

---


## 🙌 Acknowledgements

Big shoutout to the amazing team behind [Projen](https://github.com/projen/projen)!
Their groundbreaking work simplifies cloud infrastructure projects and inspires us every day. 💡

## Author

[Manuel Vogel](https://manuel-vogel.de/about/)

[![](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/manuel-vogel)
[![](https://img.shields.io/badge/GitHub-2b3137?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mavogel)
