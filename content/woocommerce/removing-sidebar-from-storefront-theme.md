Title: Removing sidebar from storefront theme
Date: 2023-02-12 21:32
Author: Sam Stoelinga
Category: WooCommerce
Tags: wordpress, woocommerce, storefront, theme
Slug: removing-sidebar-storefront-theme

By default, storefront comes with a large sidebar that isn't really
useful for ecommerce websites. This post shows you how to remove the
sidebar by creating a `functions.php` file in
your storefront child theme.

See my previous post on [creating a storefront child theme](
https://samos-it.com/posts/creating-woocommere-storefront-child-theme.html)
if you don't have a child theme yet.


Inside your child theme directory, create a file `functions.php` that
has the following content:
```php
<?php
function remove_storefront_sidebar() {
    remove_action('storefront_sidebar', 'storefront_get_sidebar', 10);
}

add_action('get_header', 'remove_storefront_sidebar');
?>
```
Note if you already have a `functions.php` file then simply append the content
above.

Afterwards, upload your new version of your theme with the updated
`functions.php` and you should now see the sidebar removed.

You might also need to update your `style.css` such that the content
is able to utilize the space where the sidebar was before.

