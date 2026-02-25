import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

type Props = {
  children: React.ReactNode;
  dark?: boolean;
};

export default function Section({ children, dark }: Props) {
  return (
    <section
      className={clsx(
        styles.section,
        dark && styles.variantSection 
      )}
    >
      <div className="container">
        {children}
      </div>
    </section>
  );
}