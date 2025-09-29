import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type DealDocument = Deal & Document;

@Schema({ collection: 'deals' })
export class Deal {
  @Prop({ required: true })
  title: string;

  @Prop()
  description?: string;

  @Prop({ required: true })
  amount: number;

  @Prop({ required: true, default: 'open' })
  status: string;
}

export const DealSchema = SchemaFactory.createForClass(Deal);