import numpy as np
import pandas as pd

np.random.seed(42)

def generate_human_samples(n):
    data = {
        'interaction_duration': np.random.normal(12, 5, n).clip(1, 40),
        'mouse_count': np.random.normal(110, 40, n).clip(10, 300),
        'mouse_speed_mean': np.random.normal(2.0, 0.8, n).clip(0.2, 6),
        'mouse_speed_variance': np.random.normal(1.0, 0.5, n).clip(0.05, 4),
        'click_count': np.random.normal(6, 3, n).clip(0, 20),
        'click_interval_variance': np.random.normal(1.0, 0.6, n).clip(0.05, 4),
        'scroll_count': np.random.normal(5, 3, n).clip(0, 20),
        'keyboard_count': np.random.normal(3, 2, n).clip(0, 15),
        'request_frequency': np.random.normal(1.5, 1.0, n).clip(0.1, 8),
        'webdriver_flag': np.random.choice([0, 1], n, p=[0.97, 0.03]),
        'touch_support': np.random.choice([0, 1], n, p=[0.6, 0.4]),
        'viewport_width': np.random.choice([1024, 1280, 1366, 1440, 1920], n),
        'viewport_height': np.random.choice([768, 800, 900, 1080], n),
        'timezone_offset': np.random.choice([-330, -300, 0, 60, 480], n),
        'hardware_concurrency': np.random.choice([2, 4, 6, 8, 12], n),
    }
    df = pd.DataFrame(data)
    df['label'] = 0  # human
    return df

def generate_bot_samples(n):
    data = {
        'interaction_duration': np.random.normal(1.5, 1.5, n).clip(0.05, 8),
        'mouse_count': np.random.normal(25, 20, n).clip(0, 100),
        'mouse_speed_mean': np.random.normal(9, 3, n).clip(2, 20),
        'mouse_speed_variance': np.random.normal(0.3, 0.3, n).clip(0.01, 2),
        'click_count': np.random.normal(3, 2, n).clip(0, 10),
        'click_interval_variance': np.random.normal(0.15, 0.2, n).clip(0.01, 1.5),
        'scroll_count': np.random.normal(1, 1.5, n).clip(0, 6),
        'keyboard_count': np.random.normal(0.5, 1, n).clip(0, 5),
        'request_frequency': np.random.normal(60, 30, n).clip(5, 150),
        'webdriver_flag': np.random.choice([0, 1], n, p=[0.35, 0.65]),
        'touch_support': np.random.choice([0, 1], n, p=[0.9, 0.1]),
        'viewport_width': np.random.choice([1024, 1280, 1366, 1920], n),
        'viewport_height': np.random.choice([768, 800, 1080], n),
        'timezone_offset': np.random.choice([-330, -300, 0, 60, 480], n),
        'hardware_concurrency': np.random.choice([2, 4, 8], n),
    }
    df = pd.DataFrame(data)
    df['label'] = 1  # bot
    return df

def generate_suspicious_samples(n):
    # Suspicious sits BETWEEN human and bot ranges, causing real overlap
    data = {
        'interaction_duration': np.random.normal(4, 2.5, n).clip(0.3, 15),
        'mouse_count': np.random.normal(55, 25, n).clip(5, 150),
        'mouse_speed_mean': np.random.normal(4.5, 2.0, n).clip(0.5, 12),
        'mouse_speed_variance': np.random.normal(0.6, 0.4, n).clip(0.02, 3),
        'click_count': np.random.normal(4, 2.5, n).clip(0, 15),
        'click_interval_variance': np.random.normal(0.5, 0.4, n).clip(0.02, 3),
        'scroll_count': np.random.normal(2.5, 2, n).clip(0, 12),
        'keyboard_count': np.random.normal(1.5, 1.5, n).clip(0, 10),
        'request_frequency': np.random.normal(10, 6, n).clip(1, 40),
        'webdriver_flag': np.random.choice([0, 1], n, p=[0.75, 0.25]),
        'touch_support': np.random.choice([0, 1], n, p=[0.75, 0.25]),
        'viewport_width': np.random.choice([1024, 1280, 1366, 1440, 1920], n),
        'viewport_height': np.random.choice([768, 800, 900, 1080], n),
        'timezone_offset': np.random.choice([-330, -300, 0, 60, 480], n),
        'hardware_concurrency': np.random.choice([2, 4, 6, 8], n),
    }
    df = pd.DataFrame(data)
    df['label'] = 2  # suspicious
    return df

print("Generating 5000 synthetic samples...")

n_human = 3000
n_bot = 1000
n_suspicious = 1000

df_human = generate_human_samples(n_human)
df_bot = generate_bot_samples(n_bot)
df_suspicious = generate_suspicious_samples(n_suspicious)

df = pd.concat([df_human, df_bot, df_suspicious], ignore_index=True)

# Add small random noise to every numeric feature to blur boundaries further
numeric_cols = [c for c in df.columns if c != 'label']
for col in numeric_cols:
    noise_scale = df[col].std() * 0.08
    df[col] = df[col] + np.random.normal(0, noise_scale, len(df))

# Randomly mislabel a small fraction of rows to simulate real-world label noise
flip_fraction = 0.03
flip_idx = np.random.choice(df.index, size=int(len(df) * flip_fraction), replace=False)
df.loc[flip_idx, 'label'] = np.random.choice([0, 1, 2], size=len(flip_idx))

# Shuffle rows
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

df.to_csv('training_data.csv', index=False)

print("✅ Saved to training_data.csv")
print(f"Dataset shape: {df.shape}")
print("\nLabel distribution:")
print(df['label'].value_counts())