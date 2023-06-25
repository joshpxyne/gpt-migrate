import Head from 'next/head';
import GroceryList from '../components/GroceryList';

export default function Home() {
  return (
    <div>
      <Head>
        <title>Grocery Store</title>
      </Head>

      <main>
        <GroceryList />
      </main>
    </div>
  );
}