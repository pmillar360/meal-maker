import '../styles/globals.css';
import type { AppProps } from 'next/app';
import Layout from '../components/Layout';
import Head from 'next/head';
import { AuthProvider } from '../context/AuthContext';
import { ToastProvider } from '../context/ToastContext';
import ToastContainer from '../components/ToastContainer';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>Meal Maker</title>
        <meta name="description" content="Find and organize recipes based on available ingredients" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <AuthProvider>
        <ToastProvider>
          <Layout>
            <Component {...pageProps} />
          </Layout>
          <ToastContainer />
        </ToastProvider>
      </AuthProvider>
    </>
  );
}

export default MyApp;
