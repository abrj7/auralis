"use client";

import { motion } from "framer-motion";
import LiquidEther from "./LiquidEther";

interface LandingPageProps {
  onGetStarted: () => void;
}

export default function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden">
      {/* LiquidEther Background */}
      <div className="absolute inset-0 w-full h-full">
        <LiquidEther
          colors={['#5227FF', '#FF9FFC', '#B19EEF']}
          mouseForce={20}
          cursorSize={100}
          isViscous={false}
          viscous={30}
          iterationsViscous={32}
          iterationsPoisson={32}
          resolution={0.5}
          isBounce={false}
          autoDemo={true}
          autoSpeed={0.5}
          autoIntensity={2.2}
          takeoverDuration={0.25}
          autoResumeDelay={3000}
          autoRampDuration={0.6}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="z-10 text-center px-4 max-w-4xl mx-auto"
      >
        <div className="mb-6 inline-block px-4 py-1.5 rounded-full bg-white/50 backdrop-blur-sm border border-white/50 text-sm font-medium text-gray-600 shadow-sm">
          Kickstarting the Future of Healthcare
        </div>
        
         <p className="text-xl md:text-2xl text-gray-600 mb-2 font-medium">
          Meet the
        </p>

        <h1 className="text-6xl md:text-8xl font-bold mb-2 tracking-tight">
          <span className="text-black">FIRST EVER</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-600 mb-2 font-medium">
          personalized AI Doctor,
        </p>

        <h1 className="text-6xl md:text-8xl font-bold mb-10 tracking-tight">
          <span className="text-gradient">AURALIS</span>
        </h1>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onGetStarted}
          className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white transition-all duration-200 bg-gray-900 rounded-full hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 shadow-lg hover:shadow-xl"
        >
          Get Started
          <svg 
            className="w-5 h-5 ml-2 -mr-1 transition-transform group-hover:translate-x-1" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </motion.button>
      </motion.div>

      {/* Decorative Elements */}
      <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent" />
    </div>
  );
}
