export const mockSubscribers = [
  {
    id: "1",
    name: "Test User",
    email: "test@example.com",
    topics: ["AI", "NLP"],
    channels: ["email", "kakao"],
  },
  {
    id: "2",
    name: "Jane Doe",
    email: "jane.doe@example.com",
    topics: ["Physics", "ML", "Robotics"],
    channels: ["email"],
  },
  {
    id: "3",
    name: "John Smith",
    email: "john.smith@example.com",
    topics: ["Data Science"],
    channels: ["email", "slack"],
  },
]

// Existing mock data for system logs
export const mockSystemLogs = [
  "Digest sent to 5 users at 8:00 AM (2025-06-09)",
  "New user subscribed: alice@example.com (2025-06-09)",
  "Digest sent to 4 users at 8:00 AM (2025-06-08)",
  "New user subscribed: bob@example.com (2025-06-08)",
  "Crawling task completed successfully (2025-06-07)",
  "Digest sent to 3 users at 8:00 AM (2025-06-07)",
]

// Existing mock data for thesis paper summaries
export const mockThesisSummaries = [
  {
    id: "t1",
    title: "Deep Learning for Medical Image Segmentation: A Novel Approach",
    authors: ["Dr. Sarah Lee", "Prof. Alex Kim"],
    summary:
      "This thesis explores advanced deep learning techniques for accurate segmentation of medical images, crucial for diagnosis and treatment planning in oncology.",
    aiSummary:
      "Leveraging U-Net architectures and attention mechanisms, this work achieves state-of-the-art performance in segmenting tumors from MRI scans, demonstrating robustness across diverse datasets and potential for clinical application.",
    publishedDate: "2024-11-15",
    categories: ["AI", "Medical Imaging", "Deep Learning", "Computer Vision"],
    sourceUrl: "https://example.edu/thesis/dl-med-seg-v1",
  },
  {
    id: "t2",
    title: "Reinforcement Learning for Autonomous Drone Navigation in Complex Environments",
    authors: ["Dr. Michael Brown", "Dr. Jessica Green"],
    summary:
      "This research focuses on developing robust reinforcement learning algorithms to enable autonomous drones to navigate and explore highly complex and dynamic environments.",
    aiSummary:
      "A novel reward function design combined with a PPO-based agent allows drones to learn optimal paths, avoid obstacles, and adapt to unforeseen changes in real-time, outperforming traditional control methods in simulated urban landscapes.",
    publishedDate: "2024-10-20",
    categories: ["Robotics", "AI", "Reinforcement Learning", "Autonomous Systems"],
    sourceUrl: "https://example.edu/thesis/rl-drone-nav-v2",
  },
  {
    id: "t3",
    title: "Natural Language Generation for Personalized Educational Content",
    authors: ["Dr. Emily White", "Prof. Daniel Clark"],
    summary:
      "This thesis investigates the use of natural language generation (NLG) models to create personalized educational materials tailored to individual student learning styles and progress.",
    aiSummary:
      "By integrating student performance data with a transformer-based NLG model, the system dynamically generates explanations, quizzes, and examples, significantly improving student engagement and comprehension in STEM subjects.",
    publishedDate: "2024-09-01",
    categories: ["NLP", "Education Technology", "AI", "Personalization"],
    sourceUrl: "https://example.edu/thesis/nlg-edu-content-v3",
  },
  {
    id: "t4",
    title: "Blockchain-Enabled Secure Data Sharing in Healthcare",
    authors: ["Dr. Olivia Taylor", "Dr. William Harris"],
    summary:
      "This work proposes a blockchain-based framework to ensure secure, transparent, and auditable sharing of sensitive patient data among healthcare providers.",
    aiSummary:
      "Utilizing a permissioned blockchain network and smart contracts, the system provides granular access control and immutability, addressing critical privacy and security concerns in health information exchange while maintaining data integrity.",
    publishedDate: "2024-08-25",
    categories: ["Blockchain", "Cybersecurity", "Healthcare IT", "Data Privacy"],
    sourceUrl: "https://example.edu/thesis/blockchain-health-data-v4",
  },
]

// New mock data for recent notifications
export const mockNotifications = [
  {
    id: "n1",
    userEmail: "test@example.com",
    channelType: "email",
    content:
      "Your daily research digest for June 9, 2025, is here! Featuring breakthroughs in AI and Quantum Computing.",
    status: "sent",
    sentAt: "2025-06-09T08:00:00Z",
  },
  {
    id: "n2",
    userEmail: "jane.doe@example.com",
    channelType: "email",
    content: "Daily digest failed to send due to invalid email address.",
    status: "failed",
    sentAt: "2025-06-09T08:01:15Z",
  },
  {
    id: "n3",
    userEmail: "test@example.com",
    channelType: "kakao",
    content: "New AI paper summary available: Deep Learning for Medical Image Segmentation.",
    status: "sent",
    sentAt: "2025-06-09T09:30:00Z",
  },
  {
    id: "n4",
    userEmail: "john.smith@example.com",
    channelType: "email",
    content: "Your personalized digest for June 8, 2025, is ready. Topics: Data Science.",
    status: "sent",
    sentAt: "2025-06-08T08:00:00Z",
  },
  {
    id: "n5",
    userEmail: "alice@example.com",
    channelType: "email",
    content: "Welcome to INSTWAVE! Your subscription is confirmed.",
    status: "sent",
    sentAt: "2025-06-09T10:15:00Z",
  },
]
