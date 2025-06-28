import React from 'react';

interface ComboboxProps {
  children: React.ReactNode;
  value: string;
  onValueChange: (value: string) => void;
}

export const Combobox: React.FC<ComboboxProps> = ({ children }) => {
  return <div>{children}</div>;
};