import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type ResumeCloseDealsDocument = ResumeCloseDeals & Document;

@Schema({ collection: 'resume_close_deals' })
export class ResumeCloseDeals {
  @Prop({ required: true })
  month: number;

  @Prop({ required: true })
  deal_stage: string;

  @Prop({ required: true })
  year: number;

  @Prop({ required: true })
  amount: number;

  @Prop({ required: true })
  count: number;
}

export const ResumeCloseDealsSchema =
  SchemaFactory.createForClass(ResumeCloseDeals);