import React, { useState } from 'react';
import { Button, Tooltip, message } from 'antd';
import { CopyOutlined, CheckOutlined } from '@ant-design/icons';

interface CopyButtonProps {
  code: string;
  size?: 'small' | 'middle' | 'large';
}

const CopyButton: React.FC<CopyButtonProps> = ({ code, size = 'small' }) => {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(code);
      } else {
        const ta = document.createElement('textarea');
        ta.value = code;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      setCopied(true);
      message.success('Copied');
      setTimeout(() => setCopied(false), 1000);
    } catch (e) {
      message.error('Copy failed');
    }
  };

  return (
    <Tooltip title={copied ? 'Copied' : 'Copy code'}>
      <Button size={size} icon={copied ? <CheckOutlined /> : <CopyOutlined />} onClick={copy} />
    </Tooltip>
  );
};

export default CopyButton;
