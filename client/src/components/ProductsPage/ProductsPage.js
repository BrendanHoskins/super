import React from 'react';
import { Container, Grid, Typography, Card, CardContent, CardMedia, CardActions, Button } from '@mui/material';

// Assume we have a list of products
const products = [
  { id: 1, name: 'Product 1', description: 'Description 1', price: 19.99, image: 'url-to-image-1' },
  { id: 2, name: 'Product 2', description: 'Description 2', price: 29.99, image: 'url-to-image-2' },
  // Add more products as needed
];

const ProductsPage = () => {
  return (
    <Container maxWidth="lg">
      <Typography variant="h2" component="h1" gutterBottom>
        Our Products
      </Typography>
      
      <Grid container spacing={4}>
        {products.map((product) => (
          <Grid item key={product.id} xs={12} sm={6} md={4}>
            <Card>
              <CardMedia
                component="img"
                height="140"
                image={product.image}
                alt={product.name}
              />
              <CardContent>
                <Typography gutterBottom variant="h5" component="div">
                  {product.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {product.description}
                </Typography>
                <Typography variant="h6" color="text.primary">
                  ${product.price.toFixed(2)}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small">Add to Cart</Button>
                <Button size="small">Learn More</Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {/* You can add pagination here if needed */}
    </Container>
  );
};

export default ProductsPage;
