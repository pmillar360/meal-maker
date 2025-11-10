import { ReactNode, useEffect, useState } from 'react';
import { FaCheckCircle, FaExclamationTriangle, FaInfoCircle, FaTimes } from 'react-icons/fa';

interface AlertProps {
  message: ReactNode;
  variant?: 'info' | 'success' | 'warning' | 'error';
  dismissible?: boolean;
  autoClose?: boolean;
  autoCloseTime?: number;
  onClose?: () => void;
}

const VARIANTS = {
  info: {
    icon: FaInfoCircle,
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-700',
    iconColor: 'text-blue-400',
  },
  success: {
    icon: FaCheckCircle,
    bgColor: 'bg-green-50',
    textColor: 'text-green-700',
    iconColor: 'text-green-400',
  },
  warning: {
    icon: FaExclamationTriangle,
    bgColor: 'bg-yellow-50',
    textColor: 'text-yellow-700',
    iconColor: 'text-yellow-400',
  },
  error: {
    icon: FaExclamationTriangle,
    bgColor: 'bg-red-50',
    textColor: 'text-red-700',
    iconColor: 'text-red-400',
  },
};

export default function Alert({ 
  message, 
  variant = 'info', 
  dismissible = true, 
  autoClose = false,
  autoCloseTime = 5000,
  onClose
}: AlertProps) {
  const [visible, setVisible] = useState(true);
  const { icon: Icon, bgColor, textColor, iconColor } = VARIANTS[variant] || VARIANTS.info;

  useEffect(() => {
    if (autoClose && visible) {
      const timer = setTimeout(() => {
        handleClose();
      }, autoCloseTime);
      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseTime, visible]);

  const handleClose = () => {
    setVisible(false);
    if (onClose) onClose();
  };

  if (!visible) return null;

  return (
    <div className={`${bgColor} ${textColor} p-4 rounded-md flex items-start`}>
      <div className={`${iconColor} shrink-0 mr-3`}>
        <Icon />
      </div>
      <div className="grow">
        {message}
      </div>
      {dismissible && (
        <button 
          onClick={handleClose}
          className={`${textColor} hover:bg-opacity-20 hover:bg-gray-500 p-1 rounded-full flex items-center justify-center ml-4`}
          title="Close"
        >
          <FaTimes size={14} />
        </button>
      )}
    </div>
  );
}
