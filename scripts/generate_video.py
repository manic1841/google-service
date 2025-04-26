import cv2
import os
import argparse


def main(args):
    # === 設定參數 ===
    image_folder = args.image_folder  # 圖片資料夾路徑
    video_name = args.output  # 輸出影片檔名
    fps = 2  # 每秒幾張圖片（可調整）

    # 取得所有圖片檔案，並依名稱排序
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    images.sort()

    if not images:
        print("There are no images in the folder.")
        return

    # 讀取第一張圖片來取得尺寸
    first_image_path = os.path.join(image_folder, images[0])
    frame = cv2.imread(first_image_path)
    height, width, layers = frame.shape
    size = (width, height)

    # 建立影片寫入器
    out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)

    print(f'Starting to create video: {video_name}')
    for image in images:
        img_path = os.path.join(image_folder, image)
        frame = cv2.imread(img_path)

        # 從檔名中解析經緯度資訊
        try:
            _, _, latitude, longitude = os.path.splitext(image)[0].split('_')
            text = f"Lat: {latitude}, Lon: {longitude}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_color = (255, 255, 255)  # 白色
            thickness = 1
            position = (10, 30)  # 右上角

            # 計算文字大小
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_width, text_height = text_size
            rect_start = (position[0] - 5, position[1] - text_height - 5)
            rect_end = (position[0] + text_width + 5, position[1] + 5)

            # 繪製灰色矩形作為背景
            frame = cv2.rectangle(frame, rect_start, rect_end, (50, 50, 50), -1)

            # 繪製文字
            frame = cv2.putText(frame, text, position, font, font_scale, font_color, thickness, cv2.LINE_AA)
        except ValueError:
            print(f"Failed to parse latitude and longitude from {image}")

        out.write(frame)
        print(f"Adding image: {image}")

    out.release()
    print("Video creation completed.")

def parse_args():
    argparser = argparse.ArgumentParser(description="Generate a video from street view images.")
    argparser.add_argument(
        "--image_folder",
        type=str,
        default="streetview_images",
        help="Folder containing street view images.",
    )
    argparser.add_argument(
        "--output",
        type=str,
        default="output/streetview_route.mp4",
        help="Output video file name.",
    )
    return argparser.parse_args()


if __name__ == "__main__":
    main(parse_args())
