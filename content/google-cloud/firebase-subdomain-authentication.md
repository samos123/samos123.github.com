Title: Firebase Authentication across subdomains
Date: 2020-11-08 22:42
Author: Sam Stoelinga
Category: Google Cloud
Tags: google cloud, gcp, openstack, kvm
Slug: deploying-openstack-on-gcp

Let's assume you have multiple applications running on
different subdomains:
- `accounts`: signing up and signing in for all applications
- `first`: Prints the first name of the signed in user
- `last`: Prints the last name of the signed in user

This model is similar to Google which redirects you to e.g.
accounts.google.com for any of the applications such as 
Gmail, Google Docs etc. In this blog post, you will learn how to set this
up using Firebase and Cloud Run.

