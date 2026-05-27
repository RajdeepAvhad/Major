import { motion } from 'framer-motion';

export default function GlassCard({ children, className = '', as = 'div', delay = 0, ...rest }) {
  const MotionTag = motion[as] || motion.div;

  return (
    <MotionTag
      className={`glass-card ${className}`.trim()}
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.35, delay }}
      {...rest}
    >
      {children}
    </MotionTag>
  );
}
