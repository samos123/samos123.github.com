Title: Creating a woocommerce storefront child theme
Date: 2023-02-11 09:34
Author: Sam Stoelinga
Category: WooCommerce
Tags: wordpress, woocommerce, storefront, theme
Slug: creating-woocommere-storefront-child-theme

The free storefront theme has a lot of features but it
doesn't look great by default. Luckily, it's quite easy to create a child
theme to make it more attractive. For example, using a child theme
you can remove the sidebar and remove the footer credits.
This blog post will guide
you to creating your child them in 2 simple steps:

1. Creating a `style.css` file with metadata about the theme
2. Packaging and uploading the theme

## Why you should use Wordpress child themes instead of directly editing theme files?
Because when you directly edit the theme files, any updates
to the parent theme will overwrite your changes. This means
all your customizations will be lost and you'll have to start
from scratch. But when you use a child theme, your customizations
are kept separate from the parent theme, so updates won't affect them.

Now that you know why, let's create the child theme

## 1. Creating a new `style.css` file with metadata
Create a new directory/folder called `mychildtheme` and change your working
directory to it:
```shell
mkdir mychildtheme
cd mychildtheme
```
Create a file `style.css` inside the `mychildtheme` directory with the following
content:
```css
/* 
Theme Name: sambal child theme of storefront
Version: 1.0 
Author: Sam Stoelinga
Author URI: https://samos-it.com
Template: storefront
*/

/* optional just an example of how you can change the style */
.product_title h1 {
    color: pink;
}
```

That's all you need for your child theme to get started. You might wonder, how
does it specify the parent theme? That's done through this line:
```
Template: storefront
```
It tells Wordpress that the parent theme of our theme is `storefront`. You can
view the theme names by listing directories under the `wp-content/themes`. In
our case there is a directory called `storefront` and that's how it finds the
parent theme.

For fun, and this is optional, I made all product titles pink. So you can see
how easy it is to add additional CSS rules to storefront this way.

## 2. Upload and activate the child theme
There are a few options to upload the child theme to your WooCommerce site:

1. Use FTP to place the `mychildtheme` directly in your `wp-content/themes`
   directory.
2. Create a zip file of the `mychildtheme` and uploading the zip file using
   the Wordpress admin UI under `/wp-admin/themes.php`

I think the zip file is the most straight forward so that's what we'll use here.

Create a zip file named `mychildtheme.zip` by running:
```sh
zip -r mychildtheme.zip mychildtheme
```

Steps to upload theme as zip:

1. Go to the following URL: `https://yourwpblog.com/wp-admin/themes.php`
2. Click on "Add Theme" button
3. Click on "Upload Theme" button
4. Click on "Choose File" button
5. Select the zip file `mychildtheme.zip` that you created before
6. Click on "Install Now" button

You should now see your new child theme and be able to preview and activate it.
Notice that any product titles are now pink due to our rule in `style.css`.
